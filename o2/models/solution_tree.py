import random
from collections import OrderedDict
from typing import TYPE_CHECKING, Optional, cast

import numpy as np
import rtree

from o2.models.settings import Settings
from o2.models.solution import Solution
from o2.pareto_front import ParetoFront
from o2.util.helper import hex_id
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
        self.solution_lookup: OrderedDict[str, Optional[Solution]] = OrderedDict()

    def add_solution(self, solution: "Solution", archive: bool = True) -> None:
        """Add a solution to the tree."""
        self.solution_lookup[solution.id] = solution
        self.rtree.insert(int(solution.id, 16), solution.point)
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
        valid_count = 0

        pareto_points = np.array([s.point for s in pareto_solutions])
        max_distances = np.array([max_distance] * len(pareto_solutions))

        neighbours, _ = self.rtree.nearest_v(  # type: ignore
            mins=pareto_points,
            maxs=pareto_points,
            num_results=1,
            max_dists=max_distances,
        )
        print_l3(f"Found {len(neighbours)} neighbours in radius {max_distance:.2f}.")
        for neighbour in neighbours:
            if error_count > 20:
                warn(f"Got too many None items from rtree! Returning None. {error_count} errors so far.")
                break
            if neighbour is None:
                warn(f"WARNING: Got None item from rtree. {error_count} errors so far.")
                error_count += 1
                continue
            item_id = hex_id(neighbour)
            if item_id not in self.solution_lookup:
                warn(
                    f"WARNING: Got non-existent solution from rtree ({item_id}). {error_count} errors so far."
                )
                error_count += 1
                continue
            solution = self.solution_lookup[item_id]
            if solution is None:
                warn(f"WARNING: Got discarded solution from rtree ({item_id}). {error_count} errors so far.")
                # TODO: How to remove the solution from the rtree?
                error_count += 1
                continue
            # Early exit if we find a pareto solution.
            # Because of reversed, it will be the most recent
            if solution in pareto_front.solutions:
                return solution

            distance = min(s.distance_to(solution) for s in pareto_front.solutions)
            # Sanity check, that the distance is smaller than the max distance.
            if distance > max_distance:
                continue
            valid_count += 1
            if distance < nearest_distance:
                nearest_solution = solution
                nearest_distance = distance

        if nearest_solution is None:
            print_l3(
                f"NO nearest solution was found in tree. ({error_count} errors, {len(neighbours)} neighbours, {len(pareto_front.solutions)} pareto solutions, {self.total_solutions} solutions in tree, {self.solutions_left} solutions unexplored)"
            )
        else:
            print_l3(f"... of which {valid_count} were valid.")
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
        nearest_solution = self.get_nearest_solution(pareto_front, max_distance=max_distance)
        if nearest_solution is not None:
            self.remove_solution(nearest_solution)
            print_l3(f"Popped solution ({nearest_solution.id})")
            if nearest_solution not in pareto_front.solutions:
                print_l3("Nearest solution is NOT in pareto front.")
            else:
                print_l3("Nearest solution is IN pareto front.")
        return nearest_solution

    def check_if_already_done(self, base_solution: "Solution", new_action: "BaseAction") -> bool:
        """Check if the given action has already been tried."""
        return Solution.hash_action_list(base_solution.actions + [new_action]) in self.solution_lookup

    def get_index_of_solution(self, solution: Solution) -> int:
        """Get the index of the solution in the tree."""
        return list(self.solution_lookup).index(solution.id)

    def get_solutions_near_to_pareto_front(
        self, pareto_front: ParetoFront, max_distance: float = float("inf")
    ) -> list["Solution"]:
        """Get a list of solutions near the pareto front."""
        bounding_points_mins = (np.array([s.point for s in pareto_front.solutions]) - max_distance).clip(
            min=0
        )
        bounding_points_maxs = np.array([s.point for s in pareto_front.solutions]) + max_distance
        solution_ids, _ = self.rtree.intersection_v(bounding_points_mins, bounding_points_maxs)
        solutions = [
            cast(Solution, self.solution_lookup[hex_id(solution_id)])
            for solution_id in set(solution_ids)
            if self.solution_lookup[hex_id(solution_id)] is not None
        ]
        # Filter out solutions, that are distanced more than max_distance
        solutions = [
            s for s in solutions if min(s.distance_to(p) for p in pareto_front.solutions) <= max_distance
        ]

        return solutions

    def get_random_solution_near_to_pareto_front(
        self, pareto_front: ParetoFront, max_distance: float = float("inf")
    ) -> Optional["Solution"]:
        """Get a random solution near the pareto front."""
        solutions = self.get_solutions_near_to_pareto_front(pareto_front, max_distance=max_distance)
        if not solutions:
            return None
        print_l3(f"Found {len(solutions)} solutions near pareto front.")
        random_solution = random.choice(solutions)
        return random_solution

    def remove_solution(self, solution: Solution) -> None:
        """Remove a solution from the tree."""
        self.rtree.delete(int(solution.id, 16), solution.point)
        self.solution_lookup[solution.id] = None

        if Settings.DUMP_DISCARDED_SOLUTIONS:
            SolutionDumper.instance.dump_solution(solution)
