from dataclasses import dataclass
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from o2.store import Store


@dataclass(frozen=True)
class Evaluation:
    df: pd.DataFrame

    total_cycle_time: float
    total_cost: float
    total_waiting_time: float
    # TODO: Think about using avg's instead of totals?

    def get_avg_waiting_time_of_task_id(self, task_id: str, store: "Store"):
        task_name = store.state.get_name_of_task(task_id)
        assert task_name is not None
        return self.get_avg_waiting_time_of_task_name(task_name)

    def get_avg_waiting_time_of_task_name(self, task_name: str) -> float:
        return self.df[self.df["Name"] == task_name]["Avg Waiting Time"].values[0]

    def get_max_waiting_time_of_task_id(self, task_id: str, store: "Store"):
        task_name = store.state.get_name_of_task(task_id)
        assert task_name is not None
        return self.get_max_waiting_time_of_task_name(task_name)

    def get_max_waiting_time_of_task_name(self, task_name: str) -> float:
        return self.df[self.df["Name"] == task_name]["Max Waiting Time"].values[0]

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
            self.total_cost >= other.total_cost
            and self.total_cycle_time >= other.total_cycle_time
        )
