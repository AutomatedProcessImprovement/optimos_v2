import math
import random
from typing import Optional

from typing_extensions import override

from o2.actions.base_actions.base_action import BaseAction, RateSelfReturnType
from o2.agents.agent import (
    ACTION_CATALOG,
    ACTION_CATALOG_BATCHING_ONLY,
    ACTION_CATALOG_LEGACY,
    Agent,
    NoNewBaseSolutionFoundError,
)
from o2.agents.tabu_agent import TabuAgent
from o2.models.self_rating import SelfRatingInput
from o2.models.solution import Solution
from o2.pareto_front import FRONT_STATUS
from o2.store import SolutionTry, Store
from o2.util.indented_printer import print_l1, print_l2
from o2.util.logger import debug

DISTANCE_MULTIPLIER = 4


class SimulatedAnnealingAgent(Agent):
    """Selects the best action to take next, based on the current state of the store."""

    @override
    def __init__(self, store: Store) -> None:
        super().__init__(store)

        self.catalog = (
            ACTION_CATALOG_LEGACY
            if store.settings.optimos_legacy_mode
            else ACTION_CATALOG_BATCHING_ONLY
            if store.settings.batching_only
            else ACTION_CATALOG
        )

        self.temperature = store.settings.sa_initial_temperature
        if self.temperature == "auto":
            # Guestimate a good starting temperature, by basically allowing all
            # points in a 4x circle around the base evaluation.
            self.temperature = (
                math.sqrt(store.base_evaluation.pareto_x**2 + store.base_evaluation.pareto_y**2)
                * DISTANCE_MULTIPLIER
            )
            print_l1(f"Auto-estimated initial temperature: {self.temperature:_}")
        if self.store.settings.sa_cooling_factor == "auto":
            number_of_iterations_to_cool = (
                self.store.settings.sa_cooling_iteration_percent * self.store.settings.max_iterations
            )
            if self.store.settings.error_radius_in_percent is None:
                raise ValueError(
                    "Settings.error_radius_in_percent is not set, so we can't auto calculate the cooling factor."
                )
            temperature_to_reach = self.store.settings.error_radius_in_percent * math.sqrt(
                store.base_evaluation.pareto_x**2 + store.base_evaluation.pareto_y**2
            )
            self.store.settings.sa_cooling_factor = (temperature_to_reach / self.temperature) ** (
                1 / number_of_iterations_to_cool
            )
            print_l1(f"Auto-estimated cooling factor: {self.store.settings.sa_cooling_factor}")

    @override
    def select_new_base_solution(self, proposed_solution_try: Optional[SolutionTry] = None) -> Solution:
        print_l2("Selecting new base evaluation...")
        print_l2(f"Old temperature: {self.temperature:_}")
        assert isinstance(self.temperature, float)
        assert isinstance(self.store.settings.sa_cooling_factor, float)
        self.temperature *= self.store.settings.sa_cooling_factor
        print_l2(f"New temperature: {self.temperature:_}")
        if proposed_solution_try is not None:
            status, solution = proposed_solution_try
            # Maybe accept bad solution
            if status == FRONT_STATUS.DOMINATES:
                # TODO: Min Distance to front
                distance = solution.distance_to(self.store.solution)
                debug(f"Discarded solution {solution.id} distance: {distance}")
                if self._accept_worse_solution(distance, self.temperature):
                    debug(f"Randomly accepted discarded solution {solution.id}.")
                    return solution

        return self._select_new_base_evaluation(
            # If the proposed solution try is None, we were called from
            # maximum non improving iterations so we don't need to reinsert
            # the current solution (which is very unlikely, as the solution
            # will be changed after every iteration, but might happen at the end
            # of the optimization)
            reinsert_current_solution=proposed_solution_try is not None
        )

    @override
    def result_callback(self, chosen_tries: list[SolutionTry], not_chosen_tries: list[SolutionTry]) -> None:
        """Call to handle the result of the evaluation."""
        pass

    def _select_new_base_evaluation(self, reinsert_current_solution: bool = False) -> Solution:
        """Select a new base evaluation."""
        if reinsert_current_solution:
            self.store.solution_tree.add_solution(self.store.solution, archive=True)

        assert isinstance(self.temperature, float)
        solution = self.store.solution_tree.get_random_solution_near_to_pareto_front(
            self.store.current_pareto_front,
            max_distance=self.temperature,
        )
        if solution is None:
            raise NoNewBaseSolutionFoundError("No new baseline evaluation found.")

        distance = self.store.current_pareto_front.avg_distance_to(solution)
        print_l2(f"Selected new random base solution {solution.id} with distance: {distance:_}")

        self.store.solution_tree.remove_solution(solution)
        return solution

    def _accept_worse_solution(self, distance: float, temperature: float) -> bool:
        """Determine whether to accept a worse solution."""
        probability = math.exp(-distance / temperature)
        return random.random() < probability
