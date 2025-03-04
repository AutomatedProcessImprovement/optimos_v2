import math
import random
from typing import Optional

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
                math.sqrt(
                    store.base_evaluation.pareto_x**2
                    + store.base_evaluation.pareto_y**2
                )
                * DISTANCE_MULTIPLIER
            )
            print_l1(f"Auto-estimated initial temperature: {self.temperature:_}")
        if self.store.settings.sa_cooling_factor == "auto":
            number_of_iterations_to_cool = (
                self.store.settings.sa_cooling_iteration_percent
                * self.store.settings.max_iterations
            )
            if self.store.settings.error_radius_in_percent is None:
                raise ValueError(
                    "Settings.error_radius_in_percent is not set, so we can't auto calculate the cooling factor."
                )
            temperature_to_reach = (
                self.store.settings.error_radius_in_percent
                * math.sqrt(
                    store.base_evaluation.pareto_x**2
                    + store.base_evaluation.pareto_y**2
                )
            )
            self.store.settings.sa_cooling_factor = (
                temperature_to_reach / self.temperature
            ) ** (1 / number_of_iterations_to_cool)
            print_l1(
                f"Auto-estimated cooling factor: {self.store.settings.sa_cooling_factor}"
            )

    def select_actions(self, store: Store) -> Optional[list[BaseAction]]:
        """Select the best actions to take next.

        It will pick at most cpu_count actions, so parallel evaluation is possible.

        If the possible options for the current base evaluation are exhausted,
        it will choose a new base evaluation.
        """
        while True:
            evaluations = TabuAgent.evaluate_rules(store)

            rating_input = SelfRatingInput.from_rule_solutions(store, evaluations)
            if rating_input is None:
                rating_input = SelfRatingInput.from_base_solution(store.solution)

            print_l1("Choosing best action...")

            # Get a list rating generators for all actions
            action_generators: list[RateSelfReturnType[BaseAction]] = [
                Action.rate_self(store, rating_input) for Action in self.catalog
            ]

            # Get valid actions from the generators, even multiple per generator,
            # if we don't have enough valid actions yet
            possible_actions = TabuAgent.get_valid_actions(store, action_generators)
            # Remove None values
            possible_actions = [
                action for action in possible_actions if action is not None
            ]

            if len(possible_actions) == 0:
                print_l1("No actions remaining, after removing Tabu & N/A actions.")
                new_solution = self._select_new_base_evaluation()
                success = new_solution is not None
                if not success:
                    print_l2("No new baseline evaluation found. Stopping.")
                    return None
                store.solution = new_solution
                continue

            sorted_actions = sorted(possible_actions, key=lambda x: x[0], reverse=True)

            number_of_actions_to_select = store.settings.max_number_of_actions_to_select
            selected_actions = sorted_actions[:number_of_actions_to_select]
            avg_rating = sum(rating for rating, _ in selected_actions) / len(
                selected_actions
            )

            print_l1(
                f"Chose {len(selected_actions)} actions with average rating {avg_rating:.1f} to evaluate."  # noqa: E501
            )

            if store.settings.print_chosen_actions:
                for rating, action in selected_actions:
                    print_l2(f"{action} with rating {rating}")

            return [action for _, action in selected_actions]

    def select_new_base_solution(
        self, proposed_solution_try: Optional[SolutionTry] = None
    ) -> Solution:
        """Select a new base solution."""
        print_l2("Selecting new base evaluation...")
        print_l2(f"Old temperature: {self.temperature:_}")
        assert isinstance(self.temperature, float)
        self.temperature *= self.store.settings.sa_cooling_factor
        print_l2(f"New temperature: {self.temperature:_}")
        if proposed_solution_try is not None:
            status, solution = proposed_solution_try
            # Maybe accept bad solution
            if status == FRONT_STATUS.DOMINATES:
                # TODO: Min Distance to front
                distance = solution.distance_to(self.store.solution)
                debug(f"Discarded solution distance: {distance}")
                if accept_worse_solution(distance, self.temperature):
                    debug("Randomly accepted discarded solution.")
                    return solution

        return self._select_new_base_evaluation()

    def _select_new_base_evaluation(self) -> Solution:
        """Select a new base evaluation."""
        assert isinstance(self.temperature, float)
        solution = self.store.solution_tree.get_random_solution_near_to_pareto_front(
            self.store.current_pareto_front,
            max_distance=self.temperature,
        )
        if solution is None:
            raise NoNewBaseSolutionFoundError("No new baseline evaluation found.")

        distance = self.store.current_pareto_front.avg_distance_to(solution)
        print_l2(f"Selected new random base solution with distance: {distance:_}")
        self.store.solution_tree.remove_solution(solution)
        return solution

    def result_callback(
        self, chosen_tries: list[SolutionTry], not_chosen_tries: list[SolutionTry]
    ) -> None:
        """Call to handle the result of the evaluation."""
        pass


def accept_worse_solution(distance: float, temperature: float) -> bool:
    """Determine whether to accept a worse solution."""
    probability = math.exp(-distance / temperature)
    return random.random() < probability
