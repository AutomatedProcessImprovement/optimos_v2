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
    ACTION_CATALOG_BATCHING_ONLY,
    ACTION_CATALOG_LEGACY,
    Agent,
)
from o2.models.rule_selector import RuleSelector
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.solution import Solution
from o2.store import SolutionTry, Store
from o2.util.indented_printer import print_l1, print_l2, print_l3


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
                else ACTION_CATALOG_BATCHING_ONLY
                if store.settings.batching_only
                else ACTION_CATALOG
            )
            # Get a list rating generators for all actions
            action_generators = [
                Action.rate_self(store, rating_input) for Action in catalog
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
                f"Chose {len(selected_actions)} actions with average rating {avg_rating} to evaluate."  # noqa: E501
            )

            if store.settings.print_chosen_actions:
                for rating, action in selected_actions:
                    print_l2(f"{action} with rating {rating}")

            return [action for _, action in selected_actions]

    def select_new_base_solution(
        self, proposed_solution_try: Optional[SolutionTry] = None
    ) -> Solution:
        """Select a new base solution.

        E.g from the SolutionTree
        """
        solution = self._select_new_base_evaluation(
            reinsert_current_solution=True,
        )
        if (
            proposed_solution_try is not None
            and proposed_solution_try[1].id == solution.id
        ):
            print_l3("Continuing with same solution as before.")
        return solution

    def _select_new_base_evaluation(
        self, reinsert_current_solution: bool = False
    ) -> Solution:
        """Choose a new base evaluation from the solution tree.

        If reinsert_current_solution is True, the current solution will be
        reinserted into the solution tree. This is useful if you aren't
        sure if you exhausted all possible actions for this solution.
        """
        print_l2("Selecting new base evaluation...")
        if reinsert_current_solution:
            self.store.solution_tree.add_solution(self.store.solution)
        new_solution = self.store.solution_tree.pop_nearest_solution(
            self.store.current_pareto_front,
            max_distance=self.store.settings.max_distance_to_new_base_solution,
        )

        if new_solution is None:
            raise Exception("No new base solutions left in the solution tree.")

        return new_solution

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
