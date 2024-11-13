from enum import Enum
from typing import TYPE_CHECKING

from rtree import index

from o2.models.evaluation import Evaluation

if TYPE_CHECKING:
    from o2.models.solution import Solution


class FRONT_STATUS(Enum):
    """The status of a solution compared to a Pareto Front."""

    IS_DOMINATED = 1
    """If the front is dominated by the evaluation"""
    DOMINATES = 2
    """If the front dominates the evaluation"""
    IN_FRONT = 3
    """If the evaluation is in the front"""
    INVALID = 4
    """If the evaluation is invalid"""


class ParetoFront:
    """A set of solutions, where no solution is dominated by another solution."""

    def __init__(self) -> None:
        self.rtree = index.Index()
        self.solutions: list["Solution"] = []
        """A list of solutions in the front. They follow the same order as the evaluations."""
        self.removed_solutions: list["Solution"] = []
        """A list of solutions that have been removed from the front, because they were dominated."""

    @property
    def size(self) -> int:
        """Return the number of solutions in the front."""
        return len(self.solutions)

    @property
    def avg_cycle_time(self) -> float:
        """Return the average cycle time of the front."""
        return (
            sum(s.evaluation.avg_cycle_time_by_case for s in self.solutions) / self.size
        )

    @property
    def avg_total_cycle_time(self) -> float:
        """Return the average total cycle time of the front."""
        return sum(s.evaluation.total_cycle_time for s in self.solutions) / self.size

    @property
    def avg_cost(self) -> float:
        """Return the average cost of the front."""
        return sum(s.evaluation.avg_cost_by_case for s in self.solutions) / self.size

    @property
    def avg_total_cost(self) -> float:
        """Return the average total cost of the front."""
        return sum(s.evaluation.total_cost for s in self.solutions) / self.size

    @property
    def avg_point(self) -> tuple[float, float]:
        """Return the average point of the front."""
        return self.avg_total_cost, self.avg_total_cycle_time

    def avg_distance_to(self, evaluation: Evaluation) -> float:
        """Return the average distance to the given evaluation."""
        return (
            sum(s.evaluation.distance_to(evaluation) for s in self.solutions)
            / self.size
        )

    def add(self, solution: "Solution") -> None:
        """Add a new solution to the front.

        Note, that this does not check if the solution is dominated by any
        other solution. This should be done before calling this method.
        """
        # Remove all solutions dominated by the new solution
        for s in self.solutions:
            if s.is_dominated_by(solution):
                self.solutions.remove(s)
                self.rtree.delete(s.id, s.evaluation.to_tuple())
                self.removed_solutions.append(s)

        self.rtree.insert(solution.id, solution.evaluation.to_tuple())
        self.solutions.append(solution)

    def is_in_front(self, solution: "Solution") -> FRONT_STATUS:
        """Check whether the evaluation is in front of the current front.

        Returns IS_DOMINATED if the front is dominated by the evaluation
        Returns DOMINATES if the front dominates the evaluation
        Returns IN_FRONT if the evaluation is in the front
        """
        if not self.solutions:
            return FRONT_STATUS.IN_FRONT

        self_is_always_dominated = True
        for s in self.solutions:
            if not s.is_dominated_by(solution):
                self_is_always_dominated = False
            if solution.is_dominated_by(s):
                return FRONT_STATUS.DOMINATES
        if self_is_always_dominated:
            return FRONT_STATUS.IS_DOMINATED
        return FRONT_STATUS.IN_FRONT

    def is_dominated_by(self, solution: "Solution") -> bool:
        """Check whether the evaluation is dominated by the current front."""
        return all(s.is_dominated_by(solution) for s in self.solutions)

    def is_dominated_by_evaluation(self, evaluation: "Evaluation") -> bool:
        """Check whether the evaluation is dominated by the current front."""
        return all(s.evaluation.is_dominated_by(evaluation) for s in self.solutions)

    def get_bounding_rect(self) -> tuple[float, float, float, float]:
        """Get the bounding rectangle of the front."""
        min_x = min(s.evaluation.total_cost for s in self.solutions)
        max_x = max(s.evaluation.total_cost for s in self.solutions)
        min_y = min(s.evaluation.total_cycle_time for s in self.solutions)
        max_y = max(s.evaluation.total_cycle_time for s in self.solutions)
        return min_x, min_y, max_x, max_y
