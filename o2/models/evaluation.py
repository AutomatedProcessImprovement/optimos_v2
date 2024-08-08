from dataclasses import dataclass
from functools import reduce
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

if TYPE_CHECKING:
    from o2.store import Store


@dataclass(frozen=True)
class Evaluation:
    global_kpis: KPIMap
    task_kpis: dict[str, KPIMap]
    resource_kpis: dict[str, ResourceKPI]
    log_info: LogInfo

    @property
    def total_cost(self) -> float:
        """Get the total cost of the simulation."""
        return self.global_kpis.cost.total

    @property
    def total_cycle_time(self) -> float:
        """Get the total cycle time of the simulation."""
        return self.global_kpis.cycle_time.total

    @property
    def total_waiting_time(self) -> float:
        """Get the total waiting time of the simulation."""
        return self.global_kpis.waiting_time.total

    @property
    def total_idle_time(self) -> float:
        """Get the total idle time of the simulation."""
        return self.global_kpis.idle_time.total

    @property
    def cases(self) -> list[Trace]:
        """Get the cases of the simulation."""
        return self.log_info.trace_list

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
        resource_utilization = [
            (resource_name, resource_kpi.utilization)
            for resource_name, resource_kpi in self.resource_kpis.items()
        ]
        return [
            resource_name
            for resource_name, _ in sorted(
                resource_utilization, key=lambda x: x[1], reverse=False
            )
        ]

    def get_tasks_sorted_by_occurrences_of_wt_and_it(self) -> list[str]:
        """Get a list of task names sorted by wt & it instances.

        In clear words: Orders the tasks by the number of times they were executed
        (number of events), which had either a waiting or idle time.
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

    def __lt__(self, other):
        return self.total_cost < other.total_cost

    def __gt__(self, other):
        return self.total_cost > other.total_cost

    def __eq__(self, other):
        return self.total_cost == other.total_cost

    def __le__(self, other):
        return self.total_cost <= other.total_cost

    def __ge__(self, other):
        return self.total_cost >= other.total_cost

    def __ne__(self, other):
        return self.total_cost != other.total_cost

    @staticmethod
    def empty():
        return Evaluation(KPIMap(), {}, {}, None)  # type: ignore

    @staticmethod
    def from_run_simulation_result(result: RunSimulationResult) -> "Evaluation":
        """Create an evaluation from a simulation result."""
        global_kpis, task_kpis, resource_kpis, log_info = result
        return Evaluation(global_kpis, task_kpis, resource_kpis, log_info)

    def __str__(self) -> str:
        return f"Cycle Time: {self.total_cycle_time}, Cost: {self.total_cost}, Waiting Time: {self.total_waiting_time}"

    # Is this evaluation dominated by another evaluation?
    # (Taking only the total cost & total cycle time into account)
    def is_dominated_by(self, other):
        """Check if this evaluation is dominated by another evaluation."""
        return (
            other.total_cost < self.total_cost
            and other.total_cycle_time < self.total_cycle_time
        )
