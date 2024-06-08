from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Evaluation:
    df: pd.DataFrame

    total_cycle_time: float
    total_cost: float
    total_waiting_time: float
    # TODO: Think about using avg's instead of totals?

    def get_waiting_time_of_task(self, task_id: str):
        return self.df[self.df["Task"] == task_id]["Waiting Time"].values[0]

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
