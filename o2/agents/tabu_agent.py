import math
from typing import Optional

from typing_extensions import override

from o2.agents.agent import (
    Agent,
    NoNewBaseSolutionFoundError,
)
from o2.models.solution import Solution
from o2.store import SolutionTry
from o2.util.indented_printer import print_l2, print_l3


class TabuAgent(Agent):
    """Selects the best action to take next, based on the current state of the store.

    This Action Selector is based on the Tabu Search algorithm, and also has options to
    support the simulated annealing.
    """

    @override
    def find_new_base_solution(self, proposed_solution_try: Optional[SolutionTry] = None) -> Solution:
        solution = self._select_new_base_evaluation(
            # If the proposed solution try is None, we were called from
            # maximum non improving iterations so we don't need to reinsert
            # the current solution
            reinsert_current_solution=proposed_solution_try is not None,
        )
        if proposed_solution_try is not None and proposed_solution_try[1].id == solution.id:
            print_l3("The proposed solution is the same as the newly found solution (see below).")
        return solution

    @override
    def result_callback(self, chosen_tries: list[SolutionTry], not_chosen_tries: list[SolutionTry]) -> None:
        pass

    def get_max_distance(self) -> float:
        """Get the maximum distance to a new base solution, aka the error radius."""
        if self.store.settings.max_distance_to_new_base_solution != float("inf"):
            return self.store.settings.max_distance_to_new_base_solution
        elif self.store.settings.error_radius_in_percent is not None:
            return self.store.settings.error_radius_in_percent * math.sqrt(
                self.store.base_evaluation.pareto_x**2 + self.store.base_evaluation.pareto_y**2
            )
        else:
            return float("inf")

    def _select_new_base_evaluation(self, reinsert_current_solution: bool = False) -> Solution:
        """Choose a new base evaluation from the solution tree.

        If reinsert_current_solution is True, the current solution will be
        reinserted into the solution tree. This is useful if you aren't
        sure if you exhausted all possible actions for this solution.
        """
        if reinsert_current_solution:
            self.store.solution_tree.add_solution(self.store.solution, archive=False)

        max_distance = self.get_max_distance()

        new_solution = self.store.solution_tree.pop_nearest_solution(
            self.store.current_pareto_front, max_distance=max_distance
        )

        if new_solution is None:
            raise NoNewBaseSolutionFoundError()

        return new_solution
