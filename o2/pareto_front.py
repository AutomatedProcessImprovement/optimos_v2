from enum import Enum
from typing import TYPE_CHECKING

from rtree import index

from o2.models.evaluation import Evaluation
from o2.util.logger import debug

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
        self.solutions: list[Solution] = []
        """A list of solutions in the front. They follow the same order as the evaluations."""

    @property
    def size(self) -> int:
        """Return the number of solutions in the front."""
        return len(self.solutions)

    @property
    def avg_y(self) -> float:
        """Return the average y of the front."""
        return sum(s.pareto_y for s in self.solutions) / self.size

    @property
    def avg_x(self) -> float:
        """Return the average x of the front."""
        return sum(s.pareto_x for s in self.solutions) / self.size

    @property
    def median_y(self) -> float:
        """Return the median y of the front."""
        return sorted(s.pareto_y for s in self.solutions)[self.size // 2]

    @property
    def median_x(self) -> float:
        """Return the median x of the front."""
        return sorted(s.pareto_x for s in self.solutions)[self.size // 2]

    @property
    def min_y(self) -> float:
        """Return the minimum y of the front."""
        return min(s.pareto_y for s in self.solutions)

    @property
    def min_x(self) -> float:
        """Return the minimum x of the front."""
        return min(s.pareto_x for s in self.solutions)

    @property
    def max_y(self) -> float:
        """Return the maximum y of the front."""
        return max(s.pareto_y for s in self.solutions)

    @property
    def max_x(self) -> float:
        """Return the maximum x of the front."""
        return max(s.pareto_x for s in self.solutions)

    @property
    def avg_per_case_cost(self) -> float:
        """Return the average cost of the front."""
        return sum(s.evaluation.avg_cost_by_case for s in self.solutions) / self.size

    @property
    def avg_total_cost(self) -> float:
        """Return the average total cost of the front."""
        return sum(s.evaluation.total_cost for s in self.solutions) / self.size

    @property
    def avg_cycle_time(self) -> float:
        """Return the average cycle time of the front."""
        return sum(s.evaluation.total_cycle_time for s in self.solutions) / self.size

    @property
    def min_cycle_time(self) -> float:
        """Return the minimum cycle time of the front."""
        return min(s.evaluation.total_cycle_time for s in self.solutions)

    @property
    def avg_point(self) -> tuple[float, float]:
        """Return the average point of the front."""
        return self.avg_x, self.avg_y

    def avg_distance_to(self, solution: "Solution") -> float:
        """Return the average distance to the given evaluation."""
        return sum(s.distance_to(solution) for s in self.solutions) / self.size

    def add(self, solution: "Solution") -> None:
        """Add a new solution to the front.

        Note, that this does not check if the solution is dominated by any
        other solution. This should be done before calling this method.
        """
        # Remove all solutions dominated by the new solution
        self.solutions = [s for s in self.solutions if not s.is_dominated_by(solution)]
        self.solutions.append(solution)

    def is_in_front(self, solution: "Solution") -> FRONT_STATUS:
        """Check whether the evaluation is in front of the current front.

        Returns IS_DOMINATED if the front is dominated by the evaluation
        Returns DOMINATES if the front dominates the evaluation
        Returns IN_FRONT if the evaluation is in the front
        """
        if not self.solutions:
            return FRONT_STATUS.IN_FRONT

        if not solution.is_valid:
            return FRONT_STATUS.INVALID

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
        min_x = min(s.pareto_x for s in self.solutions)
        max_x = max(s.pareto_x for s in self.solutions)
        min_y = min(s.pareto_y for s in self.solutions)
        max_y = max(s.pareto_y for s in self.solutions)
        return min_x, min_y, max_x, max_y
