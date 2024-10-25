import functools
import math
from dataclasses import dataclass
from functools import cached_property, reduce
from typing import TYPE_CHECKING, Counter, cast

import pandas as pd
from bpdfr_simulation_engine.execution_info import TaskEvent, Trace
from bpdfr_simulation_engine.simulation_stats_calculator import (
    KPIMap,
    LogInfo,
    ResourceKPI,
)

from o2.models.days import DAY
from o2.simulation_runner import RunSimulationResult
from o2.util.waiting_time_helper import add_waiting_times_to_event_log

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

    total_cost: float
    """Get the total cost of the simulation.

    Because this is not calculated in the simulation, we need to sum up the
    costs of all tasks.
    """

    total_cost_for_available_time: float
    """Get the total cost of the simulation.

    This takes the available time and the resource cost per hour into account.
    It will therefore give you a "realistic" of hiring the resources for the
    duration of the simulation.
    """

    avg_cost: float
    """Get the average cost of the simulation."""

    avg_cycle_time: float
    """Get the mean cycle time of the simulation."""

    avg_resource_utilization: float
    """Get the average resource utilization of the simulation."""

    avg_waiting_time: float
    """Get the average waiting time of the simulation."""

    avg_batching_waiting_time: float
    """Get the average batching waiting time per case."""

    waiting_time_per_resource: dict[str, float]
    """Get the waiting time per resource."""

    waiting_time_canvas: pd.DataFrame

    def avg_batching_waiting_time_by_task_id(self, task_id: str) -> float:
        """Get the average batching waiting time of a task."""
        result = (
            self.waiting_time_canvas[self.waiting_time_canvas["activity"] == task_id][
                "waiting_time_batching_seconds"
            ].mean()
            or 0
        )
        if result is None or math.isnan(result):
            return 0
        return result

    def total_batching_waiting_time_by_resource_id(self, resource_id: str) -> float:
        """Get the total batching waiting time of a resource (averaged by cases)."""
        result = (
            self.waiting_time_canvas[
                self.waiting_time_canvas["resource"] == resource_id
            ]
            .groupby("case")["waiting_time_batching_seconds"]
            .sum()
            .mean()
        )
        if result is None or math.isnan(result):
            return 0
        return result

    total_cycle_time: float
    """Get the total cycle time of the simulation."""

    total_waiting_time: float
    """Get the total waiting time of the simulation."""

    total_idle_time: float
    """Get the total idle time of the simulation."""

    resource_utilizations: dict[str, float]
    """Get the utilization of all resources."""

    resource_worked_times: dict[str, float]
    """Get the works time of all resources."""

    resource_available_times: dict[str, float]
    """Get the availability of all resources."""

    is_empty: bool

    global_kpis: KPIMap
    task_kpis: dict[str, KPIMap]
    resource_kpis: dict[str, ResourceKPI]
    task_execution_count_with_wt_or_it: dict[str, int]
    task_execution_counts: dict[str, int]
    enablement_weekdays: dict[str, dict[DAY, int]]

    def get_avg_waiting_time_of_task_id(self, task_id: str, store: "Store") -> float:
        """Get the average waiting time of a task."""
        return self.task_kpis[task_id].waiting_time.avg

    def get_max_waiting_time_of_task_id(self, task_id: str, store: "Store") -> float:
        """Get the maximum waiting time of a task."""
        return self.task_kpis[task_id].waiting_time.max

    def get_task_names_sorted_by_waiting_time_desc(self) -> list[str]:
        """Get a list of task names sorted by the average waiting time in desc order."""
        task_waiting_time = [
            (task_name, task_kpi.waiting_time.avg)
            for task_name, task_kpi in self.task_kpis.items()
        ]
        return [
            task_name
            for task_name, _ in sorted(
                task_waiting_time, key=lambda x: x[1], reverse=True
            )
        ]

    def get_task_names_sorted_by_idle_time_desc(self) -> list[str]:
        """Get a list of task names sorted by the average idle time in desc order."""
        task_idle_time = [
            (task_name, task_kpi.idle_time.avg)
            for task_name, task_kpi in self.task_kpis.items()
        ]
        return [
            task_name
            for task_name, _ in sorted(task_idle_time, key=lambda x: x[1], reverse=True)
        ]

    def get_most_frequent_enablement_weekdays(self, task_name: str) -> list[DAY]:
        """Get a list of weekdays, on which the task was enabled.

        The list is sorted by the most common weekday first.
        """
        return [
            day
            for day, _ in sorted(
                self.enablement_weekdays[task_name].items(),
                key=lambda x: x[1],
                reverse=True,
            )
        ]

    @staticmethod
    def get_enablement_weekdays(
        cases: list[Trace],
    ) -> dict[str, dict[DAY, int]]:
        """Get the weekdays on which a task was enabled."""
        weekdays: dict[str, dict[DAY, int]] = {}
        for case in cases:
            event_list: list[TaskEvent] = case.event_list
            for event in event_list:
                if event.task_id not in weekdays:
                    weekdays[event.task_id] = {}
                if event.enabled_datetime is None:
                    continue
                weekday = event.enabled_datetime.strftime("%A").upper()
                weekdays[event.task_id][DAY(weekday)] = (
                    weekdays[event.task_id].get(DAY(weekday), 0) + 1
                )
        return weekdays

    def get_most_frequent_resources(self, task_name: str) -> list[str]:
        """Get a list of resources that executed the task the most."""
        return self.get_resources_sorted_by_task_execution_count(task_name)

    @staticmethod
    def _get_events_for_task(cases, task_name):
        """Get all events for a task."""
        return [
            event
            for case in cases
            for event in case.event_list
            if event.task_id == task_name
        ]

    def get_least_utilized_resources(self) -> list[str]:
        """Get a list of resources that have the least utilization."""
        return [
            resource_name
            for resource_name, _ in sorted(
                self.resource_utilizations.items(), key=lambda x: x[1], reverse=False
            )
        ]

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

    def get_tasks_sorted_by_occurrences_of_wt_and_it(self) -> list[str]:
        """Get a list of task names sorted by wt & it instances.

        In clear words: Orders descending the tasks by the number of times
        they were executed(number of events) and had either a waiting or idle time.
        """
        occurrences = self.task_execution_count_with_wt_or_it
        return [
            task_name
            for task_name, _ in sorted(
                occurrences.items(), key=lambda x: x[1], reverse=True
            )
        ]

    task_execution_count_by_resource: dict[str, dict[str, int]]
    """Get the number of times each task was executed by a given resource.
    
    E.g. task_execution_count_by_resource["resource_id"]["task_id"]
    """

    def get_task_execution_count_by_resource(self, resource_id: str) -> dict[str, int]:
        """Get the number of times each task was executed by a given resource."""
        return self.task_execution_count_by_resource.get(resource_id, {})

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

    def to_tuple(self) -> tuple[float, float]:
        """Convert self to a tuple of cost for available time and total cycle time."""
        return (self.total_cost_for_available_time, self.total_cycle_time)

    def distance_to(self, other: "Evaluation") -> float:
        """Calculate the euclidean distance between two evaluations."""
        return math.sqrt(
            (self.total_cost_for_available_time - other.total_cost_for_available_time)
            ** 2
            + (self.total_cycle_time - other.total_cycle_time) ** 2
        )

    @staticmethod
    def empty():
        """Create an empty evaluation."""
        return Evaluation(
            hourly_rates={},
            total_cycle_time=0,
            total_waiting_time=0,
            total_idle_time=0,
            total_cost=0,
            total_cost_for_available_time=0,
            avg_cost=0,
            avg_cycle_time=0,
            avg_resource_utilization=0,
            avg_waiting_time=0,
            avg_batching_waiting_time=0,
            waiting_time_per_resource={},
            is_empty=True,
            resource_utilizations={},
            resource_worked_times={},
            resource_available_times={},
            global_kpis=KPIMap(),
            task_kpis={},
            resource_kpis={},
            task_execution_count_with_wt_or_it={},
            task_execution_count_by_resource={},
            task_execution_counts={},
            waiting_time_canvas=pd.DataFrame(),
            enablement_weekdays={},
        )

    @staticmethod
    def from_run_simulation_result(
        hourly_rates: HourlyRates, result: RunSimulationResult
    ) -> "Evaluation":
        """Create an evaluation from a simulation result."""
        global_kpis, task_kpis, resource_kpis, log_info = result
        cases: list[Trace] = [] if log_info is None else log_info.trace_list
        waiting_time_canvas = add_waiting_times_to_event_log(log_info)
        resource_utilizations: dict[str, float] = {
            resource_id: resource_kpi.utilization
            for resource_id, resource_kpi in resource_kpis.items()
        }

        return Evaluation(
            hourly_rates=hourly_rates,
            total_cycle_time=global_kpis.cycle_time.total,
            total_waiting_time=global_kpis.waiting_time.total,
            total_idle_time=global_kpis.idle_time.total,
            total_cost=sum(
                map(
                    lambda task_kpi: task_kpi.cost.total,
                    task_kpis.values(),
                )
            ),
            total_cost_for_available_time=sum(
                (resource_kpi.available_time / (60 * 60)) * hourly_rates[resource_id]
                for resource_id, resource_kpi in resource_kpis.items()
            ),
            avg_cost=sum(
                map(
                    lambda task_kpi: task_kpi.cost.avg,
                    task_kpis.values(),
                )
            ),
            avg_cycle_time=global_kpis.cycle_time.avg,
            avg_resource_utilization=reduce(
                lambda x, y: x + y, resource_utilizations.values()
            )
            / len(resource_utilizations),
            avg_waiting_time=global_kpis.waiting_time.avg,
            avg_batching_waiting_time=(
                waiting_time_canvas.groupby("case")["waiting_time_batching_seconds"]
                .sum()
                .mean()
                or 0
            ),
            waiting_time_per_resource=(
                waiting_time_canvas.groupby("resource")["waiting_time_batching_seconds"]
                .sum()
                .fillna(0)
                .to_dict()
            ),
            is_empty=not cases,
            resource_utilizations=resource_utilizations,
            resource_worked_times={
                resource_id: resource_kpi.worked_time
                for resource_id, resource_kpi in resource_kpis.items()
            },
            resource_available_times={
                resource_id: resource_kpi.available_time
                for resource_id, resource_kpi in resource_kpis.items()
            },
            global_kpis=global_kpis,
            task_kpis=task_kpis,
            resource_kpis=resource_kpis,
            task_execution_count_with_wt_or_it=Evaluation.get_task_execution_count_with_wt_or_it(
                cases
            ),
            task_execution_count_by_resource=Evaluation.get_task_execution_count_by_resources(
                cases
            ),
            task_execution_counts=Evaluation.get_task_execution_counts(cases),
            waiting_time_canvas=waiting_time_canvas,
            enablement_weekdays=Evaluation.get_enablement_weekdays(cases),
        )

    def __str__(self) -> str:
        return f"Cycle Time: {self.total_cycle_time}, Cost: {self.total_cost_for_available_time}, Waiting Time: {self.total_waiting_time}"

    # Is this evaluation dominated by another evaluation?
    # (Taking only the total cost & total cycle time into account)
    def is_dominated_by(self, other: "Evaluation") -> bool:
        """Check if this evaluation is dominated by another evaluation."""
        return (
            other.total_cost_for_available_time < self.total_cost_for_available_time
            and other.total_cycle_time < self.total_cycle_time
        )
