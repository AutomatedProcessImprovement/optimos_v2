from dataclasses import dataclass
from functools import reduce
from typing import TYPE_CHECKING, Counter

import pandas as pd

from o2.simulation_runner import Log
from optimos_v2.o2.models.days import DAY

if TYPE_CHECKING:
    from o2.store import Store


@dataclass(frozen=True)
class Evaluation:
    df: pd.DataFrame
    log: Log

    total_cycle_time: float
    total_cost: float
    total_waiting_time: float
    # TODO: Think about using avg's instead of totals?

    def get_avg_waiting_time_of_task_id(self, task_id: str, store: "Store") -> float:
        """Get the average waiting time of a task."""
        task_name = store.state.get_name_of_task(task_id)
        assert task_name is not None
        return self.get_avg_waiting_time_of_task_name(task_name)

    def get_avg_waiting_time_of_task_name(self, task_name: str) -> float:
        """Get the average waiting time of a task."""
        return self.df[self.df["Name"] == task_name]["Avg Waiting Time"].values[0]

    def get_max_waiting_time_of_task_id(self, task_id: str, store: "Store") -> float:
        """Get the maximum waiting time of a task."""
        task_name = store.state.get_name_of_task(task_id)
        assert task_name is not None
        return self.get_max_waiting_time_of_task_name(task_name)

    def get_max_waiting_time_of_task_name(self, task_name: str) -> float:
        """Get the maximum waiting time of a task."""
        return self.df[self.df["Name"] == task_name]["Max Waiting Time"].values[0]

    def get_task_names_sorted_by_waiting_time_desc(self) -> list[str]:
        """Get a list of task names sorted by the average waiting time in desc order."""
        return self.df.sort_values(by="Avg Waiting Time", ascending=False)[
            "Name"
        ].tolist()

    def _get_log_entries_for_task(self, task_name: str):
        return filter(lambda log_entry: log_entry.activity == task_name, self.log)

    def get_most_frequent_enablement_weekdays(self, task_name: str) -> list[DAY]:
        """Get a list of weekdays, on which the task was enabled.

        The list is sorted by the most common weekday first.
        """
        log_entries = self._get_log_entries_for_task(task_name)
        enablement_weekdays = map(
            lambda log_entry: log_entry.enabled.strftime("%A")
            if log_entry.enabled
            else None,
            log_entries,
        )
        counter = Counter(enablement_weekdays)
        return [DAY[day.upper()] for day, _ in counter.most_common() if day is not None]

    def get_most_frequent_resources(self, task_name: str) -> list[str]:
        """Get a list of resources that executed the task the most."""
        log_entries = self._get_log_entries_for_task(task_name)
        resource_names = map(lambda log_entry: log_entry.resource, log_entries)
        counter = Counter(resource_names)
        return [
            resource for resource, _ in counter.most_common() if resource is not None
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
        return Evaluation(pd.DataFrame(), float("inf"), float("inf"), float("inf"))

    def __str__(self) -> str:
        return f"Cycle Time: {self.total_cycle_time}, Cost: {self.total_cost}, Waiting Time: {self.total_waiting_time}"

    # Is this evaluation dominated by another evaluation?
    # (Taking only the total cost & total cycle time into account)
    def is_dominated_by(self, other):
        return (
            other.total_cost < self.total_cost
            and other.total_cycle_time < self.total_cycle_time
        )
