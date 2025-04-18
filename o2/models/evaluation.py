import math
from collections import Counter
from dataclasses import dataclass
from functools import cached_property, reduce
from typing import TYPE_CHECKING, Callable, cast

import pandas as pd
from prosimos.execution_info import TaskEvent, Trace
from prosimos.simulation_stats_calculator import (
    KPIMap,
    ResourceKPI,
)

from o2.models.days import DAY
from o2.models.settings import CostType, Settings
from o2.simulation_runner import RunSimulationResult
from o2.util.helper import lambdify_dict
from o2.util.waiting_time_helper import (
    BatchInfo,
    BatchInfoKey,
    SimpleBatchInfo,
    get_batches_from_event_log,
)

if TYPE_CHECKING:
    from o2.models.timetable import TimetableType
    from o2.store import Store


HourlyRates = dict[str, int]


@dataclass(frozen=True)
class Evaluation:
    """An evaluation of a simulation run.

    It's a wrapper for the result classes of a PROSIMOS simulation run,
    with a lot of useful getters and methods to analyze the results.
    """

    hourly_rates: HourlyRates

    task_kpis: dict[str, KPIMap]
    resource_kpis: dict[str, ResourceKPI]

    avg_cycle_time_by_case: float
    """Get the mean cycle time of the simulation."""

    avg_waiting_time_by_case: float
    """Get the average waiting time of the simulation."""

    avg_batching_waiting_time_by_case: float
    """Get the average batching waiting time per case."""

    avg_batching_waiting_time_per_task: dict[str, float]
    """Get the average batching waiting time per task."""
    total_batching_waiting_time_per_task: dict[str, float]
    """Get the total batching waiting time per task (all cases)."""

    total_duration: float
    """Get the total duration (processing + idle) of the simulation."""

    sum_of_durations: float
    """Get the sum of all task durations of the simulation."""

    sum_of_cycle_times: float
    """Get the sum of all task cycle times of the simulation."""

    total_batching_waiting_time: float
    """Get the total batching waiting time of the simulation (all cases)."""

    total_batching_waiting_time_per_resource: dict[str, float]
    """Get the total batching waiting time of the simulation per resource."""

    total_cycle_time: float
    """Get the total cycle time of the simulation."""

    total_processing_time: float
    """Get the total processing time of the simulation."""

    total_waiting_time: float
    """Get the total waiting time of the simulation."""

    task_execution_count_by_resource: dict[str, dict[str, int]]
    """Get the number of times each task was executed by a given resource.

    E.g. task_execution_count_by_resource["resource_id"]["task_id"]
    """

    is_empty: bool
    """Is this evaluation based on an empty simulation run?"""

    task_execution_count_with_wt_or_it: dict[str, int]
    """Get the count each task was executed with a waiting or idle time."""

    task_execution_counts: dict[str, int]
    """Get the count each task was executed"""

    task_enablement_weekdays: dict[str, dict[DAY, dict[int, int]]]
    """Get the weekdays & hours on which a task was enabled."""

    task_started_weekdays: dict[str, dict[DAY, dict[int, int]]]
    """Get the weekdays & hours on which a task was started."""

    resource_allocation_ratio_task: dict[str, float]
    """Get the allocation ratio of each task."""

    total_fixed_cost_by_task: dict[str, float]
    """Get the total fixed cost of each task."""
    avg_fixed_cost_per_case: float
    """Get the average fixed cost per case."""

    batches_by_activity_with_idle: dict[str, list[SimpleBatchInfo]]
    """Get the batches grouped by activity, only including those with idle time."""

    avg_batch_size_for_batch_enabled_tasks: float
    """Get the average batch size over all batches."""

    avg_batch_size_per_task: dict[str, float]
    """Get the average batch size per task."""

    avg_idle_wt_per_task_instance: float
    """Get the average idle waiting time per task instance."""

    avg_batch_processing_time_per_task_instance: float
    """Get the average batch processing time per task instance.
    
    Pseudo-Code:
    sum(batch.processing_time for batch in batches) / sum(batch.size for batch in batches)
    """

    resource_started_weekdays: dict[str, dict[DAY, dict[int, int]]]
    """Get the weekdays & hours on which a resource started any task."""

    tasks_by_number_of_duplicate_enablement_dates: dict[str, int]
    """Get the tasks sorted by the number of duplicate enablement dates."""

    @cached_property
    def total_processing_cost_for_tasks(self) -> float:
        """Get the total cost of all tasks."""
        return sum(
            map(
                lambda task_kpi: task_kpi.cost.total,
                self.task_kpis.values(),
            )
        )

    @cached_property
    def total_cost_for_worked_time(self) -> float:
        """Get the total flexible cost of the simulation.

        This takes the worked time and the resource cost per hour into account.
        It will therefore give you a "realistic" of hiring the resources for the
        duration of the simulation.
        """
        return sum(
            (resource_kpi.worked_time / (60 * 60)) * self.hourly_rates[resource_id]
            for resource_id, resource_kpi in self.resource_kpis.items()
        )

    @cached_property
    def total_cost_for_available_time(self) -> float:
        """Get the cost of the resources for the worked time.

        Aka the cost you had if the resource calender would exactly match the
        worked time.
        """
        return sum(
            (resource_kpi.available_time / (60 * 60)) * self.hourly_rates[resource_id]
            for resource_id, resource_kpi in self.resource_kpis.items()
        )

    @cached_property
    def avg_cost_by_case(self) -> float:
        """Get the average cost sum of all tasks."""
        return sum(
            map(
                lambda task_kpi: task_kpi.cost.avg,
                self.task_kpis.values(),
            )
        )

    @cached_property
    def avg_resource_utilization_by_case(self) -> float:
        """Get the average resource utilization of the simulation."""
        return reduce(lambda x, y: x + y, self.resource_utilizations.values()) / len(
            self.resource_utilizations
        )

    @cached_property
    def resource_worked_times(self) -> dict[str, float]:
        """Get the worked time of all resources."""
        return {
            resource_id: resource_kpi.worked_time for resource_id, resource_kpi in self.resource_kpis.items()
        }

    @cached_property
    def resource_available_times(self) -> dict[str, float]:
        """Get the availability of all resources."""
        return {
            resource_id: resource_kpi.available_time
            for resource_id, resource_kpi in self.resource_kpis.items()
        }

    @cached_property
    def resource_utilizations(self) -> dict[str, float]:
        """Get the utilization of all resources."""
        return {
            resource_id: resource_kpi.utilization for resource_id, resource_kpi in self.resource_kpis.items()
        }

    @cached_property
    def total_fixed_cost(self) -> float:
        """Get the total fixed cost of the simulation."""
        return sum(self.total_fixed_cost_by_task.values())

    @cached_property
    def total_cost(self) -> float:
        """Get the total cost of the simulation."""
        return self.total_cost_for_worked_time + self.total_fixed_cost

    @cached_property
    def total_resource_idle_time(self) -> float:
        """Get the total resource idle time of the simulation.

        This is calculated by summing up the difference worked time and available time
        for all resources.
        """
        return sum(
            resource_kpi.worked_time - resource_kpi.available_time
            for resource_kpi in self.resource_kpis.values()
        )

    @cached_property
    def total_task_idle_time(self) -> float:
        """Get the total task idle time of the simulation."""
        return sum(task_kpi.idle_time.total for task_kpi in self.task_kpis.values())

    @property
    def pareto_x(self) -> float:
        """Get the cost used for positioning the evaluation in the pareto front.

        NOTE: This is depended on the global, static setting found in `Settings.COST_TYPE`
        """
        if Settings.COST_TYPE == CostType.FIXED_COST:
            return self.total_fixed_cost
        elif Settings.COST_TYPE == CostType.RESOURCE_COST:
            return self.total_cost_for_available_time
        elif Settings.COST_TYPE == CostType.TOTAL_COST:
            return self.total_cost_for_worked_time
        elif Settings.COST_TYPE == CostType.WAITING_TIME_AND_PROCESSING_TIME:
            return self.total_processing_time
        elif Settings.COST_TYPE == CostType.AVG_WT_AND_PT_PER_TASK_INSTANCE:
            return self.avg_batch_processing_time_per_task_instance
        raise ValueError(f"Unknown cost type: {Settings.COST_TYPE}")

    @property
    def pareto_y(self) -> float:
        """Get the duration used for positioning the evaluation in the pareto front."""
        if Settings.COST_TYPE == CostType.WAITING_TIME_AND_PROCESSING_TIME:
            return self.total_waiting_time + self.total_task_idle_time
        elif Settings.COST_TYPE == CostType.AVG_WT_AND_PT_PER_TASK_INSTANCE:
            return self.avg_idle_wt_per_task_instance
        return self.total_duration

    def get_avg_waiting_time_of_task_id(self, task_id: str) -> float:
        """Get the average waiting time of a task."""
        return self.task_kpis[task_id].waiting_time.avg

    def get_total_waiting_time_of_task_id(self, task_id: str) -> float:
        """Get the total waiting time of a task."""
        return self.task_kpis[task_id].waiting_time.total

    def get_max_waiting_time_of_task_id(self, task_id: str) -> float:
        """Get the maximum waiting time of a task."""
        return self.task_kpis[task_id].waiting_time.max

    def get_task_names_sorted_by_waiting_time_desc(self) -> list[str]:
        """Get a list of task names sorted by the average waiting time in desc order."""
        task_waiting_time = [
            (task_name, task_kpi.waiting_time.avg) for task_name, task_kpi in self.task_kpis.items()
        ]
        return [task_name for task_name, _ in sorted(task_waiting_time, key=lambda x: x[1], reverse=True)]

    def get_task_names_sorted_by_idle_time_desc(self) -> list[str]:
        """Get a list of task names sorted by the average idle time in desc order."""
        task_idle_time = [
            (task_name, task_kpi.idle_time.avg) for task_name, task_kpi in self.task_kpis.items()
        ]
        return [task_name for task_name, _ in sorted(task_idle_time, key=lambda x: x[1], reverse=True)]

    def get_most_frequent_enablement_weekdays(self, task_name: str) -> list[DAY]:
        """Get a list of weekdays, on which the task was enabled.

        The list is sorted by the most common weekday first.
        """
        return [
            day
            for day, _ in sorted(
                self.task_enablement_weekdays[task_name].items(),
                key=lambda x: sum(x[1].values()),
                reverse=True,
            )
        ]

    def get_most_frequent_resources(self, task_name: str) -> list[str]:
        """Get a list of resources that executed the task the most."""
        return self.get_resources_sorted_by_task_execution_count(task_name)

    def get_least_utilized_resources(self) -> list[str]:
        """Get a list of resources that have the least utilization."""
        return [
            resource_name
            for resource_name, _ in sorted(
                self.resource_utilizations.items(), key=lambda x: x[1], reverse=False
            )
        ]

    def get_tasks_sorted_by_occurrences_of_wt_and_it(self) -> list[str]:
        """Get a list of task names sorted by wt & it instances.

        In clear words: Orders descending the tasks by the number of times
        they were executed(number of events) and had either a waiting or idle time.
        """
        occurrences = self.task_execution_count_with_wt_or_it
        return [task_name for task_name, _ in sorted(occurrences.items(), key=lambda x: x[1], reverse=True)]

    def get_task_execution_count_by_resource(self, resource_id: str) -> dict[str, int]:
        """Get the number of times each task was executed by a given resource."""
        return self.task_execution_count_by_resource.get(resource_id, {})

    def get_avg_processing_cost_per_task(self) -> dict[str, float]:
        """Get the average processing cost per task."""
        return {task_id: task_kpi.cost.avg for task_id, task_kpi in self.task_kpis.items()}

    def get_avg_cost_per_task(self) -> dict[str, float]:
        """Get the average total (fixed + processing) cost per task."""
        return {
            task_id: task_kpi.cost.avg + (self.total_fixed_cost_by_task.get(task_id, 0) / task_kpi.cost.count)
            for task_id, task_kpi in self.task_kpis.items()
        }

    def get_total_cost_per_task(self) -> dict[str, float]:
        """Get the total (fixed + processing) cost per task."""
        return {
            task_id: task_kpi.cost.total + self.total_fixed_cost_by_task.get(task_id, 0)
            for task_id, task_kpi in self.task_kpis.items()
        }

    def get_resources_sorted_by_task_execution_count(self, task_id: str) -> list[str]:
        """Get a list of resource_ids, that executed the given task.

        The list is sorted by the most common resource first.
        """
        resource_counts = Counter(
            {
                resource_id: count[task_id]
                for resource_id, count in self.task_execution_count_by_resource.items()
                if task_id in count
            }
        )

        # Return the resource_ids sorted by most common first
        return [resource_id for resource_id, _ in resource_counts.most_common()]

    def get_total_processing_time_per_task(self) -> dict[str, float]:
        """Get the total processing time per task (excl. idle times)."""
        return {task_id: task_kpi.processing_time.total for task_id, task_kpi in self.task_kpis.items()}

    def get_average_processing_time_per_task(self) -> dict[str, float]:
        """Get the average processing time per task (excl. idle times)."""
        return {task_id: task_kpi.processing_time.avg for task_id, task_kpi in self.task_kpis.items()}

    def get_total_duration_time_per_task(self) -> dict[str, float]:
        """Get the total duration time per task (incl. idle times)."""
        return {task_id: task_kpi.idle_processing_time.total for task_id, task_kpi in self.task_kpis.items()}

    def get_avg_duration_time_per_task(self) -> dict[str, float]:
        """Get the average duration time per task (incl. idle times & wt)."""
        return {
            task_id: task_kpi.idle_processing_time.avg + task_kpi.waiting_time.avg
            for task_id, task_kpi in self.task_kpis.items()
        }

    def get_total_idle_time_of_task_id(self, task_id: str) -> float:
        """Get the total idle time of a task."""
        return self.task_kpis[task_id].idle_time.total

    def get_total_cycle_time_of_task_id(self, task_id: str) -> float:
        """Get the total cycle time of a task."""
        return self.task_kpis[task_id].idle_cycle_time.total

    def to_tuple(self) -> tuple[float, float]:
        """Convert self to a tuple of cost for available time and total cycle time."""
        return (self.pareto_x, self.pareto_y)

    def distance_to(self, other: "Evaluation") -> float:
        """Calculate the euclidean distance between two evaluations."""
        return math.sqrt((self.pareto_x - other.pareto_x) ** 2 + (self.pareto_y - other.pareto_y) ** 2)

    # Is this evaluation dominated by another evaluation?
    # (Taking only the total cost & total cycle time into account)
    def is_dominated_by(self, other: "Evaluation") -> bool:
        """Check if this evaluation is dominated by another evaluation."""
        if not Settings.EQUAL_DOMINATION_ALLOWED:
            return other.pareto_x <= self.pareto_x and other.pareto_y <= self.pareto_y
        return other.pareto_x < self.pareto_x and other.pareto_y < self.pareto_y

    def __str__(self) -> str:
        """Return a string representation of the evaluation."""
        return f"{Settings.get_pareto_x_label()}: {self.pareto_x:.1f}, {Settings.get_pareto_y_label()}: {self.pareto_y:.1f}"  # noqa: E501

    @staticmethod
    def get_task_enablement_weekdays(
        cases: list[Trace],
    ) -> dict[str, dict[DAY, dict[int, int]]]:
        """Get the weekdays & time of day on which a task was enabled."""
        weekdays: dict[str, dict[DAY, dict[int, int]]] = {}
        for case in cases:
            event_list: list[TaskEvent] = case.event_list
            for event in event_list:
                if event.task_id not in weekdays:
                    weekdays[event.task_id] = {}
                if event.enabled_datetime is None:
                    continue
                day = DAY.from_date(event.enabled_datetime)
                hour = event.enabled_datetime.hour
                if day not in weekdays[event.task_id]:
                    weekdays[event.task_id][day] = {}
                if hour not in weekdays[event.task_id][day]:
                    weekdays[event.task_id][day][hour] = 0
                weekdays[event.task_id][day][hour] += 1
        return weekdays

    @staticmethod
    def get_task_started_at_weekdays(
        cases: list[Trace],
    ) -> dict[str, dict[DAY, dict[int, int]]]:
        """Get the weekdays & time of day on which a task was started."""
        weekdays: dict[str, dict[DAY, dict[int, int]]] = {}
        for case in cases:
            event_list: list[TaskEvent] = case.event_list
            for event in event_list:
                if event.task_id not in weekdays:
                    weekdays[event.task_id] = {}
                if event.started_datetime is None:
                    continue
                day = DAY.from_date(event.started_datetime)
                hour = event.started_datetime.hour
                if day not in weekdays[event.task_id]:
                    weekdays[event.task_id][day] = {}
                if hour not in weekdays[event.task_id][day]:
                    weekdays[event.task_id][day][hour] = 0
                weekdays[event.task_id][day][hour] += 1
        return weekdays

    @staticmethod
    def _get_events_for_task(cases: list[Trace], task_name: str) -> list[TaskEvent]:
        """Get all events for a task."""
        return [event for case in cases for event in case.event_list if event.task_id == task_name]

    @staticmethod
    def get_resource_started_weekdays(
        cases: list[Trace],
    ) -> dict[str, dict[DAY, dict[int, int]]]:
        """Get the weekdays & time of day on which a resource started a(/any) task."""
        return {
            resource_id: {
                DAY(weekday): {hour: count for hour, count in task_start_times.items()}
                for _, resource_start_times in task_start_times_by_day.items()
                for weekday, task_start_times in resource_start_times.items()
            }
            for resource_id, task_start_times_by_day in Evaluation.get_resource_task_started_weekdays(
                cases
            ).items()
        }

    @staticmethod
    def get_task_execution_counts(cases) -> dict[str, int]:
        """Get the count each task was executed."""
        occurrences: dict[str, int] = {}
        for case in cases:
            for event in cast(list[TaskEvent], case.event_list):
                occurrences[event.task_id] = occurrences.get(event.task_id, 0) + 1
        return occurrences

    @staticmethod
    def get_task_execution_count_with_wt_or_it(cases: list[Trace]) -> dict[str, int]:
        """Get the count each task was executed with a waiting or idle time."""
        occurrences: dict[str, int] = {}
        for case in cases:
            for event in cast(list[TaskEvent], case.event_list):
                if event.waiting_time is not None and event.waiting_time > 0:
                    occurrences[event.task_id] = occurrences.get(event.task_id, 0) + 1
                if event.idle_time is not None and event.idle_time > 0:
                    occurrences[event.task_id] = occurrences.get(event.task_id, 0) + 1
        return occurrences

    @staticmethod
    def get_task_execution_count_by_resources(
        cases: list[Trace],
    ) -> dict[str, dict[str, int]]:
        """Get the number of times each task was executed by a given resource."""
        occurrences: dict[str, dict[str, int]] = {}
        for case in cases:
            event_list: list[TaskEvent] = case.event_list
            for event in cast(list[TaskEvent], event_list):
                occurrences[event.resource_id] = occurrences.get(event.resource_id, {})
                occurrences[event.resource_id][event.task_id] = (
                    occurrences[event.resource_id].get(event.task_id, 0) + 1
                )
        return occurrences

    @staticmethod
    def get_resource_task_started_weekdays(
        cases: list[Trace],
    ) -> dict[str, dict[str, dict[DAY, dict[int, int]]]]:
        """Get the weekdays & time of day on which a task was started by a resource."""
        weekdays: dict[str, dict[str, dict[DAY, dict[int, int]]]] = {}
        for case in cases:
            event_list: list[TaskEvent] = case.event_list
            for event in event_list:
                if event.resource_id not in weekdays:
                    weekdays[event.resource_id] = {}
                if event.task_id not in weekdays[event.resource_id]:
                    weekdays[event.resource_id][event.task_id] = {}
                if event.started_datetime is None:
                    continue
                day = DAY.from_date(event.started_datetime)
                hour = event.started_datetime.hour
                if day not in weekdays[event.resource_id][event.task_id]:
                    weekdays[event.resource_id][event.task_id][day] = {}
                if hour not in weekdays[event.resource_id][event.task_id][day]:
                    weekdays[event.resource_id][event.task_id][day][hour] = 0
                weekdays[event.resource_id][event.task_id][day][hour] += 1
        return weekdays

    @staticmethod
    def get_resource_allocation_ratio(
        cases: list[Trace],
    ) -> dict[str, float]:
        """Get the allocation ratio of each task.

        The allocation ratio is calculated =
        (number of unique resources that executed the task) / (total number of resources)
        """
        resources_total = set()
        resources_per_task: dict[str, set[str]] = {}
        for case in cases:
            event_list: list[TaskEvent] = case.event_list
            for event in event_list:
                resources_per_task[event.task_id] = resources_per_task.get(event.task_id, set())
                resources_per_task[event.task_id].add(event.resource_id)
                resources_total.add(event.resource_id)

        return {
            task_id: len(resources) / len(resources_total)
            for task_id, resources in resources_per_task.items()
        }

    @staticmethod
    def get_tasks_by_number_of_duplicate_enablement_dates(
        cases: list[Trace],
    ) -> dict[str, int]:
        """Get the tasks sorted by the number of duplicate enablement dates.

        Meaning the more often the same task is enabled at the same time, the higher the rank.
        The granularity is one hour.
        NOTE: tasks with only one enablement at a given time are not considered.
        """
        tasks_with_enablement_dates: dict[str, dict[DAY, dict[int, int]]] = dict()
        for case in cases:
            event_list: list[TaskEvent] = case.event_list
            for event in event_list:
                if event.task_id not in tasks_with_enablement_dates:
                    tasks_with_enablement_dates[event.task_id] = {}
                if event.started_datetime is None:
                    continue
                day = DAY.from_date(event.started_datetime)
                hour = event.started_datetime.hour
                if day not in tasks_with_enablement_dates[event.task_id]:
                    tasks_with_enablement_dates[event.task_id][day] = {}
                if hour not in tasks_with_enablement_dates[event.task_id][day]:
                    tasks_with_enablement_dates[event.task_id][day][hour] = 0
                tasks_with_enablement_dates[event.task_id][day][hour] += 1

        return {
            task_id: sum(
                sum(count for count in day_counts.values() if count > 1)
                for day_counts in tasks_with_enablement_dates[task_id].values()
            )
            for task_id in tasks_with_enablement_dates
        }

    @staticmethod
    def get_batches_by_activity_with_idle(
        batches: dict[BatchInfoKey, BatchInfo],
    ) -> dict[str, list[SimpleBatchInfo]]:
        """Get batches grouped by activity, only including those with idle time.

        Returns a dict where:
        - key: activity name
        - value: list of dicts containing only the essential batch info:
            {
                'accumulation_begin': datetime,
                'start': datetime,
                'ideal_proc': float,
                'idle_time': float
            }
        """
        result: dict[str, list[SimpleBatchInfo]] = {}
        for batch in batches.values():
            if batch["idle_time"] == 0:
                continue

            activity = batch["activity"]
            if activity not in result:
                result[activity] = []

            result[activity].append(
                {
                    "accumulation_begin": batch["accumulation_begin"],
                    "start": batch["start"],
                    "ideal_proc": batch["ideal_proc"],
                    "idle_time": batch["idle_time"],
                }
            )

        return result

    @staticmethod
    def get_average_batch_size_per_task(
        batches: dict[BatchInfoKey, BatchInfo],
    ) -> dict[str, float]:
        """Get the average batch size per task."""
        batches_by_task = {}
        for batch in batches.values():
            task_id = batch["activity"]
            if task_id not in batches_by_task:
                batches_by_task[task_id] = []
            batches_by_task[task_id].append(batch)

        return {
            task_id: sum(batch["size"] for batch in batches) / len(batches)
            for task_id, batches in batches_by_task.items()
        }

    @staticmethod
    def get_avg_batch_size_for_batch_enabled_tasks(
        batches: dict[BatchInfoKey, BatchInfo],
    ) -> float:
        """Get the average batch size over all batches."""
        if not batches:
            return 0
        return sum(batch["size"] for batch in batches.values()) / len(batches)

    @staticmethod
    def empty():
        """Create an empty evaluation."""
        return Evaluation(
            hourly_rates={},
            total_duration=0,
            total_cycle_time=0,
            avg_cycle_time_by_case=0,
            is_empty=True,
            task_kpis={},
            resource_kpis={},
            task_execution_count_with_wt_or_it={},
            task_execution_count_by_resource={},
            task_execution_counts={},
            task_enablement_weekdays={},
            task_started_weekdays={},
            avg_batching_waiting_time_per_task={},
            total_batching_waiting_time_per_task={},
            total_batching_waiting_time_per_resource={},
            avg_batching_waiting_time_by_case=0,
            total_batching_waiting_time=0,
            avg_waiting_time_by_case=0,
            total_waiting_time=0,
            total_processing_time=0,
            sum_of_durations=0,
            sum_of_cycle_times=0,
            total_fixed_cost_by_task={},
            avg_fixed_cost_per_case=0,
            resource_allocation_ratio_task={},
            batches_by_activity_with_idle={},
            avg_batch_size_per_task={},
            avg_batch_size_for_batch_enabled_tasks=0,
            resource_started_weekdays={},
            tasks_by_number_of_duplicate_enablement_dates={},
            avg_idle_wt_per_task_instance=0,
            avg_batch_processing_time_per_task_instance=0,
        )

    @staticmethod
    def from_run_simulation_result(
        hourly_rates: HourlyRates,
        fixed_cost_fns: dict[str, Callable[[float], float]],
        batching_rules_exist: bool,
        result: RunSimulationResult,
    ) -> "Evaluation":
        """Create an evaluation from a simulation result."""
        global_kpis, task_kpis, resource_kpis, log_info = result
        cases: list[Trace] = [] if log_info is None else log_info.trace_list

        all_cases_are_non_empty = all([len(trace.event_list) > 0 for trace in log_info.trace_list])
        if not all_cases_are_non_empty:
            return Evaluation.empty()

        batches = get_batches_from_event_log(log_info, fixed_cost_fns, batching_rules_exist)

        batches_greater_than_one = {
            batch_key: batch for batch_key, batch in batches.items() if batch["size"] > 1
        }

        batch_pd = pd.DataFrame(
            (
                {
                    "batch_id": batch["batch_id"],
                    "activity": batch["activity"],
                    "case": batch["case"],
                    "resource": batch["resource"],
                    "batch_size": batch["size"],
                    "batch_waiting_time_seconds": batch["wt_batching"],
                    "fixed_cost": batch["fixed_cost"],
                    "processing_time": batch["ideal_proc"],
                }
                for batch in batches.values()
            ),
            columns=[
                "batch_id",
                "activity",
                "case",
                "resource",
                "batch_size",
                "batch_waiting_time_seconds",
                "fixed_cost",
                "processing_time",
            ],
        )

        total_fixed_cost_by_task = batch_pd.groupby("activity")["fixed_cost"].sum().fillna(0).to_dict()

        avg_fixed_cost_per_case = batch_pd.groupby("case")["fixed_cost"].sum().mean()

        first_enablement = min(
            [event.enabled_datetime for trace in log_info.trace_list for event in trace.event_list],
            default=log_info.started_at,
        )
        last_completion = max(
            [event.completed_datetime for trace in log_info.trace_list for event in trace.event_list],
            default=log_info.ended_at,
        )
        total_cycle_time = (last_completion - first_enablement).total_seconds()
        total_idle_time = sum(
            [kpi.idle_time.total for kpi in task_kpis.values() if kpi.idle_time.total is not None]
        )
        total_processing_time = sum(
            [kpi.processing_time.total for kpi in task_kpis.values() if kpi.processing_time.total is not None]
        )

        total_duration = total_idle_time + total_processing_time

        # Caculate the average processing time per task_instance
        # This means that we take sum of processing times per unique batch and divide by the number of task_instances
        # Which in this case can be achivied by taking the sum of batch sizes
        task_instance_count = batch_pd.groupby("batch_id")["batch_size"].first().sum()
        if task_instance_count > 0:
            avg_batch_processing_time_per_task_instance = (
                batch_pd.groupby("batch_id")["processing_time"].first().sum() / task_instance_count
            )
            avg_idle_wt_per_task_instance = (
                sum(kpi.idle_time.total + kpi.waiting_time.total for kpi in task_kpis.values())
                / task_instance_count
            )

        else:
            avg_batch_processing_time_per_task_instance = 0
            avg_idle_wt_per_task_instance = 0

        sum_of_durations = sum(
            [
                kpi.idle_processing_time.total
                for kpi in task_kpis.values()
                if kpi.idle_processing_time.total is not None
            ]
        )

        sum_of_cycle_times = sum(
            [kpi.idle_cycle_time.total for kpi in task_kpis.values() if kpi.idle_cycle_time.total is not None]
        )

        # print("\n".join([f"{event.started_datetime.isoformat()} -> {event.completed_datetime.isoformat()} (enabled: {event.enabled_datetime.isoformat()}) (I:{event.idle_time / 3600}, P:{event.processing_time/3600}, WT:{event.waiting_time/3600}, C:{event.cycle_time / 3600})" for trace in log_info.trace_list for event in trace.event_list]))
        return Evaluation(
            hourly_rates=hourly_rates,
            total_duration=total_duration,
            total_cycle_time=total_cycle_time,
            total_waiting_time=global_kpis.waiting_time.total,
            avg_cycle_time_by_case=global_kpis.cycle_time.avg,
            avg_waiting_time_by_case=global_kpis.waiting_time.avg,
            avg_idle_wt_per_task_instance=avg_idle_wt_per_task_instance,
            avg_batch_processing_time_per_task_instance=avg_batch_processing_time_per_task_instance,
            total_processing_time=total_processing_time,
            sum_of_durations=sum_of_durations,
            sum_of_cycle_times=sum_of_cycle_times,
            is_empty=not cases,
            task_kpis=task_kpis,
            resource_kpis=resource_kpis,
            task_execution_count_with_wt_or_it=Evaluation.get_task_execution_count_with_wt_or_it(cases),
            task_execution_count_by_resource=Evaluation.get_task_execution_count_by_resources(cases),
            task_execution_counts=Evaluation.get_task_execution_counts(cases),
            task_enablement_weekdays=Evaluation.get_task_enablement_weekdays(cases),
            task_started_weekdays=Evaluation.get_task_started_at_weekdays(cases),
            resource_allocation_ratio_task=Evaluation.get_resource_allocation_ratio(cases),
            avg_batching_waiting_time_per_task=(
                batch_pd.groupby("activity")["batch_waiting_time_seconds"].mean().fillna(0).to_dict()
            ),
            total_batching_waiting_time_per_task=(
                batch_pd.groupby("activity")["batch_waiting_time_seconds"].sum().fillna(0).to_dict()
            ),
            total_batching_waiting_time_per_resource=(
                batch_pd.groupby("resource")["batch_waiting_time_seconds"].sum().fillna(0).to_dict()
            ),
            avg_batching_waiting_time_by_case=(batch_pd["batch_waiting_time_seconds"].mean()),
            total_batching_waiting_time=(batch_pd["batch_waiting_time_seconds"].sum()),
            total_fixed_cost_by_task=total_fixed_cost_by_task,
            avg_fixed_cost_per_case=avg_fixed_cost_per_case,
            batches_by_activity_with_idle=Evaluation.get_batches_by_activity_with_idle(
                batches_greater_than_one
            ),
            avg_batch_size_per_task=Evaluation.get_average_batch_size_per_task(batches_greater_than_one),
            avg_batch_size_for_batch_enabled_tasks=Evaluation.get_avg_batch_size_for_batch_enabled_tasks(
                batches_greater_than_one
            ),
            resource_started_weekdays=Evaluation.get_resource_started_weekdays(cases),
            tasks_by_number_of_duplicate_enablement_dates=Evaluation.get_tasks_by_number_of_duplicate_enablement_dates(
                cases
            ),
        )
