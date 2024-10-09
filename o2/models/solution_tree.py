from typing import TYPE_CHECKING, Optional, cast

import rtree

from o2.models.solution import Solution
from o2.pareto_front import ParetoFront

if TYPE_CHECKING:
    from o2.actions.base_action import BaseAction


class SolutionTree:
    """The SolutionTree class is a tree of solutions.

    It's used to get a list of possible base solutions, that can be used to try
    new actions on. Those base states are sorted by their distance to the
    current Pareto Front (Nearest Neighbor).

    The points in the pareto front are of course therefore always chosen first.

    Under the hood it uses a RTree to store the solutions, which allows for fast
    nearest neighbor queries, as well as insertions / deletions.
    """

    def __init__(self) -> None:
        self.rtree = rtree.index.Index()
        self.discarded_solutions: list[Solution] = []
        self.solution_lookup: dict[int, Solution] = {}

    def add_solution(self, solution: "Solution") -> None:
        """Add a solution to the tree."""
        self.solution_lookup[solution.id] = solution
        self.rtree.insert(solution.id, solution.point)

    def get_nearest_solution(self, pareto_front: ParetoFront) -> Optional["Solution"]:
        """Get the nearest solution to the given Pareto Front.

        This means the solution with the smallest distance to any solution in the
        given Pareto Front. With the distance being the euclidean distance of the
        evaluations on the time & cost axis.
        """
        nearest_solution: Optional[Solution] = None
        nearest_distance = float("inf")
        for pareto_solution in pareto_front.solutions:
            item = next(
                self.rtree.nearest(pareto_solution.point, 1, objects=True), None
            )
            if item is None:
                continue
            solution = self.solution_lookup[item.id]
            distance = solution.evaluation.distance_to(solution.evaluation)
            if distance < nearest_distance:
                nearest_solution = solution
                nearest_distance = distance
        return nearest_solution

    def pop_nearest_solution(self, pareto_front: ParetoFront) -> Optional["Solution"]:
        """Pop the nearest solution to the given Pareto Front."""
        nearest_solution = self.get_nearest_solution(pareto_front)
        if nearest_solution is not None:
            self.rtree.delete(nearest_solution.id, nearest_solution.point)
            self.discarded_solutions.append(nearest_solution)
        return nearest_solution

    def check_if_already_done(
        self, base_solution: "Solution", new_action: "BaseAction"
    ) -> bool:
        """Check if the given action has already been tried."""
        return (
            Solution.hash_action_list(base_solution.actions + [new_action])
            in self.solution_lookup
        )
