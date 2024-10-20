from collections import OrderedDict
from typing import TYPE_CHECKING, Optional, cast

import rtree

from o2.models.solution import Solution
from o2.pareto_front import ParetoFront
from o2.util.indented_printer import print_l3

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
        self.solution_lookup = OrderedDict()

    def add_solution(self, solution: "Solution") -> None:
        """Add a solution to the tree."""
        self.solution_lookup[solution.id] = solution
        self.rtree.insert(solution.id, solution.point)

    def get_nearest_solution(
        self, pareto_front: ParetoFront, max_distance: float = float("inf")
    ) -> Optional["Solution"]:
        """Get the nearest solution to the given Pareto Front.

        This means the solution with the smallest distance to any solution in the
        given Pareto Front. With the distance being the euclidean distance of the
        evaluations on the time & cost axis.

        If there are still pareto solutions left, it will usually return the
        most recent one. If there are no pareto solutions left, it will return
        """
        nearest_solution: Optional[Solution] = None
        nearest_distance = float("inf")
        for pareto_solution in reversed(pareto_front.solutions):
            item = next(
                self.rtree.nearest(pareto_solution.point, 1, objects=True), None
            )
            if item is None:
                continue
            solution = self.solution_lookup[item.id]
            distance = pareto_solution.evaluation.distance_to(solution.evaluation)
            # Early exit if we find a pareto solution.
            # Because of reversed, it will be the most recent
            if distance == 0:
                return solution
            if distance < nearest_distance and distance <= max_distance:
                nearest_solution = solution
                nearest_distance = distance
        return nearest_solution

    def pop_nearest_solution(
        self, pareto_front: ParetoFront, max_distance: float = float("inf")
    ) -> Optional["Solution"]:
        """Pop the nearest solution to the given Pareto Front."""
        nearest_solution = self.get_nearest_solution(
            pareto_front, max_distance=max_distance
        )
        if nearest_solution is not None:
            self.rtree.delete(nearest_solution.id, nearest_solution.point)
            self.discarded_solutions.append(nearest_solution)
            print_l3(
                f"Popped solution. {len(self.solution_lookup) - len(self.discarded_solutions)} solutions left. ({len(self.discarded_solutions)} exhausted so far)"  # noqa: E501
            )
            if nearest_solution not in pareto_front.solutions:
                print_l3("Nearest solution is NOT in pareto front.")
            else:
                print_l3("Nearest solution is IN pareto front.")
        return nearest_solution

    def check_if_already_done(
        self, base_solution: "Solution", new_action: "BaseAction"
    ) -> bool:
        """Check if the given action has already been tried."""
        return (
            Solution.hash_action_list(base_solution.actions + [new_action])
            in self.solution_lookup
        )

    def get_index_of_solution(self, solution: Solution) -> int:
        """Get the index of the solution in the tree."""
        return list(self.solution_lookup).index(solution.id)
