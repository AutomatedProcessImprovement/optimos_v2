import concurrent.futures
import traceback
from typing import Optional

from o2.actions.base_action import BaseAction, RateSelfReturnType
from o2.actions.remove_rule_action import (
    RemoveRuleAction,
    RemoveRuleActionParamsType,
)
from o2.agents.agent import (
    ACTION_CATALOG,
    ACTION_CATALOG_LEGACY,
    Agent,
)
from o2.models.rule_selector import RuleSelector
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.solution import Solution
from o2.store import Store
from o2.util.indented_printer import print_l1, print_l2


class TabuAgent(Agent):
    """Selects the best action to take next, based on the current state of the store.

    This Action Selector is based on the Tabu Search algorithm, and also has options to
    support the simulated annealing.
    """

    def select_actions(self, store: Store) -> Optional[list[BaseAction]]:  # noqa: D102
        while True:
            evaluations = TabuAgent.evaluate_rules(store)

            rating_input = SelfRatingInput.from_rule_solutions(store, evaluations)
            if rating_input is None:
                rating_input = SelfRatingInput.from_base_solution(store.solution)

            print_l1("Choosing best action...")
            catalog = (
                ACTION_CATALOG_LEGACY
                if store.settings.optimos_legacy_mode
                else ACTION_CATALOG
            )
            # Get a list rating generators for all actions
            action_generators = [
                Action.rate_self(store, rating_input) for Action in catalog
            ]

            # Get valid actions from the generators, even multiple per generator,
            # if we don't have enough valid actions yet
            possible_actions = TabuAgent._get_valid_actions(store, action_generators)
            # Remove None values
            possible_actions = [
                action for action in possible_actions if action is not None
            ]

            if len(possible_actions) == 0:
                print_l1("No actions remaining, after removing Tabu & N/A actions.")
                print_l2("Choosing new baseline evaluation.")
                success = store.choose_new_base_evaluation() is not None
                if not success:
                    print_l2("No new baseline evaluation found. Stopping.")
                    return None
                continue

            sorted_actions = sorted(possible_actions, key=lambda x: x[0], reverse=True)

            number_of_actions_to_select = store.settings.max_number_of_actions_to_select
            selected_actions = sorted_actions[:number_of_actions_to_select]
            avg_rating = sum(rating for rating, _ in selected_actions) / len(
                selected_actions
            )

            print_l1(
                f"Chose {len(selected_actions)} actions with average rating {avg_rating} to evaluate."  # noqa: E501
            )

            if store.settings.print_chosen_actions:
                for rating, action in selected_actions:
                    print_l2(f"{action} with rating {rating}")

            return [action for _, action in selected_actions]

    # Removes every firing rule individually and evaluates the new state
    @staticmethod
    def evaluate_rules(
        store: "Store",
        skip_size_rules: bool = False,
    ) -> dict[RuleSelector, Solution]:
        """Evaluate the impact of removing each rule individually.

        You may skip size rules, because they are required in many scenarios,
        so for e.g. testing certain actions set this to true.
        """
        batching_rules = store.solution.state.timetable.batch_processing
        # TODO: Find a smart way to see which rules not to evaluate,
        #  when all possible actions are already in the tabu list
        # # tabu_indices = [action.params["rule_hash"] for action in store.tabu_list]
        #  type: ignore # TODO FIX Type

        # # Only allow rules, that can be decreased / modified in size
        # batching_rules = [
        #     rule
        #     for i, rule in enumerate(batching_rules)
        #     if rule.can_be_modified(store, -1) and rule.id() not in tabu_indices
        # ]

        if store.settings.optimos_legacy_mode:
            # Disable rule evaluation in legacy mode
            return {}

        firing_rule_selectors = [
            RuleSelector(rule.task_id, (or_index, and_index))
            for rule in batching_rules
            for or_index, or_rule in enumerate(rule.firing_rules)
            for and_index, _ in enumerate(or_rule)
            if rule.can_remove_firing_rule(or_index, and_index)
        ]

        if len(batching_rules) == 0:
            return {}

        evaluations: dict[RuleSelector, Solution] = {}

        # Determine the number of threads to use
        num_threads = store.settings.max_threads
        chunk_size = max(1, len(firing_rule_selectors) // num_threads)

        # Split the indices of the rules into chunks
        chunks = [
            firing_rule_selectors[i : i + chunk_size]
            for i in range(0, len(firing_rule_selectors), chunk_size)
        ]

        if store.settings.disable_parallel_evaluation:
            for chunk in chunks:
                for rule_selector in chunk:
                    solution = Solution.from_parent(
                        store.solution,
                        RemoveRuleAction(
                            RemoveRuleActionParamsType(rule=rule_selector)
                        ),
                    )
                    evaluations[solution.last_action.params["rule"]] = solution  # type: ignore
            return evaluations

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures: list[concurrent.futures.Future[Solution]] = []
            for chunk in chunks:
                for rule_selector in chunk:
                    futures.append(
                        executor.submit(
                            Solution.from_parent,
                            store.solution,
                            RemoveRuleAction(
                                RemoveRuleActionParamsType(rule=rule_selector)
                            ),
                        )
                    )

            for future in concurrent.futures.as_completed(futures):
                try:
                    solution = future.result()
                    # TODO Fix Type
                    evaluations[solution.last_action.params["rule"]] = solution  # type: ignore
                except Exception as e:
                    print_l1(f"Error in future: {e}")
                    print_l2(traceback.format_exc())
                    continue

        return evaluations

    @staticmethod
    def _get_valid_actions(
        store: "Store",
        action_generators: list[RateSelfReturnType],
    ) -> list[tuple[RATING, BaseAction]]:
        """Get settings.number_of_actions_to_select valid actions from the generators.

        If the action is tabu, it will skip it and try the next one.
        If the action is not applicable, it will not try more

        It will take into account the `settings.only_allow_low_last` setting,
        to first select non RATING.LOW actions first.
        """
        actions = []
        low_actions = []
        generators_queue = action_generators.copy()

        while len(generators_queue) > 0:
            action_generator = generators_queue.pop(0)
            if isinstance(action_generator, tuple):
                continue

            for rating, action in action_generator:
                if rating == RATING.NOT_APPLICABLE or action is None:
                    break
                if store.is_tabu(action):
                    continue
                if not action.check_if_valid(store):
                    continue
                if store.settings.only_allow_low_last and rating == RATING.LOW:
                    low_actions.append((rating, action))
                else:
                    actions.append((rating, action))
                if len(actions) >= store.settings.max_number_of_actions_to_select:
                    return actions
                else:
                    generators_queue.append(action_generator)
                    break
        if len(actions) == 0:
            return low_actions
        return actions
