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

    global_kpis: KPIMap
    task_kpis: dict[str, KPIMap]
    resource_kpis: dict[str, ResourceKPI]
    log_info: LogInfo

    @cached_property
    def waiting_time_canvas(self) -> pd.DataFrame:
        """Get the waiting time canvas of the simulation."""
        return add_waiting_times_to_event_log(self.log_info)

    @cached_property
    def total_cost(self) -> float:
        """Get the total cost of the simulation.

        Because this is not calculated in the simulation, we need to sum up the
        costs of all tasks.
        """
        return sum(
            map(
                lambda task_kpi: task_kpi.cost.total,
                self.task_kpis.values(),
            )
        )

    @cached_property
    def total_cost_for_available_time(self) -> float:
        """Get the total cost of the simulation.

        This takes the available time and the resource cost per hour into account.
        It will therefore give you a "realistic" of hiring the resources for the
        duration of the simulation.
        """
        return sum(
            (resource_kpi.available_time / (60 * 60)) * self.hourly_rates[resource_id]
            for resource_id, resource_kpi in self.resource_kpis.items()
        )

    @cached_property
    def avg_cost(self) -> float:
        """Get the average cost of the simulation."""
        return sum(
            map(
                lambda task_kpi: task_kpi.cost.avg,
                self.task_kpis.values(),
            )
        )

    @cached_property
    def avg_cycle_time(self) -> float:
        """Get the mean cycle time of the simulation."""
        return self.global_kpis.cycle_time.avg

    @cached_property
    def avg_resource_utilization(self) -> float:
        """Get the average resource utilization of the simulation."""
        return reduce(lambda x, y: x + y, self.resource_utilizations.values()) / len(
            self.resource_utilizations
        )

    @cached_property
    def avg_waiting_time(self) -> float:
        """Get the average waiting time of the simulation."""
        return self.global_kpis.waiting_time.avg

    @cached_property
    def avg_batching_waiting_time(self) -> float:
        """Get the average batching waiting time per case."""
        return (
            self.waiting_time_canvas.groupby("case")["waiting_time_batching_seconds"]
            .sum()
            .mean()
            or 0
        )

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

    @cached_property
    def total_cycle_time(self) -> float:
        """Get the total cycle time of the simulation."""
        return self.global_kpis.cycle_time.total

    @cached_property
    def total_waiting_time(self) -> float:
        """Get the total waiting time of the simulation."""
        return self.global_kpis.waiting_time.total

    @cached_property
    def total_idle_time(self) -> float:
        """Get the total idle time of the simulation."""
        return self.global_kpis.idle_time.total

    @cached_property
    def cases(self) -> list[Trace]:
        """Get the cases of the simulation."""
        if self.log_info is None:
            return []
        return self.log_info.trace_list or []

    @cached_property
    def is_empty(self) -> bool:
        """Check if the evaluation is empty."""
        return not self.cases

    @cached_property
    def resource_utilizations(self) -> dict[str, float]:
        """Get the utilization of all resources."""
        return {
            resource_id: resource_kpi.utilization
            for resource_id, resource_kpi in self.resource_kpis.items()
        }

    @cached_property
    def resource_worked_times(self) -> dict[str, float]:
        """Get the works time of all resources."""
        return {
            resource_id: resource_kpi.worked_time
            for resource_id, resource_kpi in self.resource_kpis.items()
        }

    @cached_property
    def resource_available_times(self) -> dict[str, float]:
        """Get the availability of all resources."""
        return {
            resource_id: resource_kpi.available_time
            for resource_id, resource_kpi in self.resource_kpis.items()
        }

    # TODO: Think about using avg's instead of totals?

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

    def _get_all_events(self) -> list[TaskEvent]:
        """Get all task events from all traces."""
        return [event for trace in self.cases for event in trace.event_list]

    def _get_events_for_task(self, task_id: str):
        """Get all task events for a specific task."""
        return [event for event in self._get_all_events() if event.task_id == task_id]

    def _get_events_for_resource(self, resource_id: str):
        """Get all task events for a specific resource."""
        return [
            event
            for event in self._get_all_events()
            if event.resource_id == resource_id
        ]

    def get_most_frequent_enablement_weekdays(self, task_name: str) -> list[DAY]:
        """Get a list of weekdays, on which the task was enabled.

        The list is sorted by the most common weekday first.
        """
        events = self._get_events_for_task(task_name)
        enablement_weekdays = map(
            lambda event: event.enabled_datetime.strftime("%A")
            if event.enabled_datetime
            else None,
            events,
        )
        counter = Counter(enablement_weekdays)
        return [DAY[day.upper()] for day, _ in counter.most_common() if day is not None]

    def get_most_frequent_resources(self, task_name: str) -> list[str]:
        """Get a list of resources that executed the task the most."""
        events = self._get_events_for_task(task_name)
        resource_names = map(lambda event: event.resource_id, events)
        counter = Counter(resource_names)
        return [
            resource for resource, _ in counter.most_common() if resource is not None
        ]

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
        occurrences: dict[str, int] = {}
        for case in self.cases:
            for event in cast(list[TaskEvent], case.event_list):
                if event.waiting_time is not None and event.waiting_time > 0:
                    occurrences[event.task_id] = occurrences.get(event.task_id, 0) + 1
                if event.idle_time is not None and event.idle_time > 0:
                    occurrences[event.task_id] = occurrences.get(event.task_id, 0) + 1
        return [
            task_name
            for task_name, _ in sorted(
                occurrences.items(), key=lambda x: x[1], reverse=True
            )
        ]

    def get_task_execution_count_by_resource(self, resource_id: str) -> dict[str, int]:
        """Get the number of times each task was executed by a given resource."""
        events = self._get_events_for_resource(resource_id)
        counter = Counter(map(lambda event: event.task_id, events))
        return dict(counter)

    def get_resources_sorted_by_task_execution_count(self, task_id: str) -> list[str]:
        """Get list of resources sorted by the number of times they executed a task.

        The list is sorted by the most common resource first.
        """
        events = self._get_events_for_task(task_id)
        counter = Counter(map(lambda event: event.resource_id, events))
        return [
            resource
            for resource, _ in sorted(counter.items(), key=lambda x: x[1], reverse=True)
        ]

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
        return Evaluation({}, KPIMap(), {}, {}, None)  # type: ignore

    @staticmethod
    def from_run_simulation_result(
        hourly_rates: HourlyRates, result: RunSimulationResult
    ) -> "Evaluation":
        """Create an evaluation from a simulation result."""
        global_kpis, task_kpis, resource_kpis, log_info = result
        return Evaluation(hourly_rates, global_kpis, task_kpis, resource_kpis, log_info)

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
