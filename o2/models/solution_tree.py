import random
from collections import OrderedDict
from typing import TYPE_CHECKING, Optional, cast

import rtree

from o2.models.settings import Settings
from o2.models.solution import Solution
from o2.pareto_front import ParetoFront
from o2.util.indented_printer import print_l1, print_l3
from o2.util.logger import warn
from o2.util.solution_dumper import SolutionDumper

if TYPE_CHECKING:
    from o2.actions.base_actions.base_action import BaseAction


class SolutionTree:
    """The SolutionTree class is a tree of solutions.

    It's used to get a list of possible base solutions, that can be used to try
    new actions on. Those base states are sorted by their distance to the
    current Pareto Front (Nearest Neighbor).

    The points in the pareto front are of course therefore always chosen first.

    Under the hood it uses a RTree to store the solutions, which allows for fast
    nearest neighbor queries, as well as insertions / deletions.
    """

    def __init__(
        self,
    ) -> None:
        self.rtree = rtree.index.Index()
        self.solution_lookup: OrderedDict[int, Optional[Solution]] = OrderedDict()

    def add_solution(self, solution: "Solution", archive: bool = True) -> None:
        """Add a solution to the tree."""
        self.solution_lookup[solution.id] = solution
        self.rtree.insert(solution.id, solution.point)
        if archive and not solution.is_base_solution and Settings.ARCHIVE_SOLUTIONS:
            solution.archive()

    def add_solution_as_discarded(self, solution: "Solution") -> None:
        """Add a solution to the tree as discarded."""
        self.solution_lookup[solution.id] = None
        if Settings.DUMP_DISCARDED_SOLUTIONS:
            SolutionDumper.instance.dump_solution(solution)

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
        pareto_solutions = list(reversed(pareto_front.solutions))
        error_count = 0
        while len(pareto_solutions) > 0:
            if error_count > 20:
                warn("Got too many None items from rtree! Returning None.")
                break
            pareto_solution = pareto_solutions[0]
            item = next(
                self.rtree.nearest(pareto_solution.point, 1, objects=True), None
            )
            if item is None:
                warn("WARNING: Got None item from rtree.")
                error_count += 1
                continue
            solution = self.solution_lookup[item.id]

            if item.id in self.solution_lookup and solution is None:
                warn("WARNING: Got discarded solution from rtree.")
                self.rtree.delete(item.id, item.bbox)
                error_count += 1
                continue

            if solution is None:
                warn("WARNING: Got non-existent solution from rtree.")
                error_count += 1
                continue

            distance = pareto_solution.distance_to(solution)
            # Early exit if we find a pareto solution.
            # Because of reversed, it will be the most recent
            if distance == 0:
                return solution
            if distance < nearest_distance and distance <= max_distance:
                nearest_solution = solution
                nearest_distance = distance
            pareto_solutions.pop(0)
        if nearest_solution is None:
            print_l3(
                f"NO nearest solution was found in tree, for the given Pareto Front (size: {len(pareto_front.solutions)})."
            )
        return nearest_solution

    @property
    def discarded_solutions(self) -> int:
        """Return the number of discarded / exhausted solutions."""
        return sum(1 for id in self.solution_lookup if self.solution_lookup[id] is None)

    @property
    def solutions_left(self) -> int:
        """Return the number of untried solutions left in the tree."""
        return len(self.solution_lookup) - self.discarded_solutions

    @property
    def total_solutions(self) -> int:
        """Return the total number of solutions (tried + non-tried)."""
        return len(self.solution_lookup)

    def pop_nearest_solution(
        self, pareto_front: ParetoFront, max_distance: float = float("inf")
    ) -> Optional["Solution"]:
        """Pop the nearest solution to the given Pareto Front."""
        nearest_solution = self.get_nearest_solution(
            pareto_front, max_distance=max_distance
        )
        if nearest_solution is not None:
            self.remove_solution(nearest_solution)
            len_discarded_solutions = self.discarded_solutions
            print_l3(
                f"Popped solution. {self.total_solutions - len_discarded_solutions} solutions left. ({len_discarded_solutions} exhausted so far)"  # noqa: E501
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

    def get_solutions_near_to_pareto_front(
        self, pareto_front: ParetoFront, max_distance: float = float("inf")
    ) -> list["Solution"]:
        """Get a list of solutions near the pareto front."""
        bounding_rect = pareto_front.get_bounding_rect()
        bounding_rect_with_distance = (
            bounding_rect[0] - max_distance,
            bounding_rect[1] - max_distance,
            bounding_rect[2] + max_distance,
            bounding_rect[3] + max_distance,
        )
        items = self.rtree.intersection(bounding_rect_with_distance, objects=True)
        solutions: list["Solution"] = [
            cast(Solution, self.solution_lookup[item.id])
            for item in items
            if self.solution_lookup[item.id] is not None
        ]

        return solutions

    def get_random_solution_near_to_pareto_front(
        self, pareto_front: ParetoFront, max_distance: float = float("inf")
    ) -> Optional["Solution"]:
        """Get a random solution near the pareto front."""
        solutions = self.get_solutions_near_to_pareto_front(
            pareto_front, max_distance=max_distance
        )
        if not solutions:
            return None
        print_l3(f"Found {len(solutions)} solutions near pareto front.")
        random_solution = random.choice(solutions)
        return random_solution

    def remove_solution(self, solution: Solution) -> None:
        """Remove a solution from the tree."""
        self.rtree.delete(solution.id, solution.point)
        self.solution_lookup[solution.id] = None

        if Settings.DUMP_DISCARDED_SOLUTIONS:
            SolutionDumper.instance.dump_solution(solution)
