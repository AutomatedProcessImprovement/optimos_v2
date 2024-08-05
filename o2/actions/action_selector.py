import concurrent.futures
import os
from typing import Optional, Type

from o2.actions.add_week_day_rule_action import AddWeekDayRuleAction
from o2.actions.base_action import BaseAction
from o2.actions.modify_calendar_by_wt_action import ModifyCalendarByWTAction
from o2.actions.modify_daily_hour_rule_action import ModifyDailyHourRuleAction
from o2.actions.modify_large_wt_rule_action import ModifyLargeWtRuleAction
from o2.actions.modify_ready_wt_rule_action import ModifyReadyWtRuleAction
from o2.actions.modify_size_rule_action import (
    ModifySizeRuleAction,
)
from o2.actions.remove_rule_action import (
    RemoveRuleAction,
    RemoveRuleActionParamsType,
)
from o2.constants import OPTIMOS_LEGACY_MODE
from o2.models.constraints import RULE_TYPE
from o2.models.evaluation import Evaluation
from o2.models.rule_selector import RuleSelector
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.state import State
from o2.pareto_front import FRONT_STATUS
from o2.store import Store
from o2.util.indented_printer import print_l1, print_l2

ACTION_CATALOG: list[Type[BaseAction]] = [
    AddWeekDayRuleAction,
    # TODO Disabled for now for tests
    # ModifyCalendarByWTAction,
    ModifyDailyHourRuleAction,
    ModifyLargeWtRuleAction,
    ModifyReadyWtRuleAction,
    ModifySizeRuleAction,
    RemoveRuleAction,
]

if OPTIMOS_LEGACY_MODE:
    ACTION_CATALOG = [
        ModifyCalendarByWTAction,
    ]

# TODO: Try out multiple Actions at once


class ActionSelector:
    """Selects the best action to take next, based on the current state of the store."""

    @staticmethod
    def select_action(store: Store) -> Optional[BaseAction]:
        """Select the best action to take next."""
        evaluations = ActionSelector.evaluate_rules(store)

        rating_input = SelfRatingInput.from_rule_evaluations(store, evaluations)
        if rating_input is None:
            rating_input = SelfRatingInput.from_base_evaluation(
                store.current_fastest_evaluation
            )

        print_l1("Choosing best action...")
        # Get a list of rated, possible actions
        possible_actions = [
            Action.rate_self(store, rating_input) for Action in ACTION_CATALOG
        ]

        possible_actions = [
            (rating, action)
            for rating, action in possible_actions
            if rating != RATING.NOT_APPLICABLE
            and action is not None
            and not store.is_tabu(action)
        ]

        if len(possible_actions) == 0:
            print_l1("No actions remaining, after removing Tabu & N/A actions...")
            return None

        rating, best_action = max(possible_actions, key=lambda x: x[0])
        if rating == 0:
            return None
        print_l1(f"Chose with Rating: {rating}:")
        print_l2(str(best_action))
        return best_action

    # Removes every firing rule individually and evaluates the new state
    @staticmethod
    def evaluate_rules(
        store: "Store",
        skip_size_rules: bool = False,
    ) -> dict[RuleSelector, Evaluation]:
        """Evaluate the impact of removing each rule individually.

        You may skip size rules, because they are required in many scenarios,
        so for e.g. testing certain actions set this to true.
        """
        batching_rules = store.state.timetable.batch_processing
        # TODO: Find a smart way to see which rules not to evaluate,
        #  when all possible actions are already in the tabu list
        # # tabu_indices = [action.params["rule_hash"] for action in store.tabu_list]
        #  type: ignore TODO FIX Type

        # # Only allow rules, that can be decreased / modified in size
        # batching_rules = [
        #     rule
        #     for i, rule in enumerate(batching_rules)
        #     if rule.can_be_modified(store, -1) and rule.id() not in tabu_indices
        # ]

        if OPTIMOS_LEGACY_MODE:
            # Disable rule evaluation in legacy mode
            return {}

        firing_rule_selectors = [
            RuleSelector(rule.task_id, (or_index, and_index))
            for rule in batching_rules
            for or_index, or_rule in enumerate(rule.firing_rules)
            for and_index, _ in enumerate(or_rule)
            if not skip_size_rules
            or rule.firing_rules[or_index][and_index].attribute != RULE_TYPE.SIZE
        ]

        if len(batching_rules) == 0:
            return {}

        evaluations: dict[RuleSelector, Evaluation] = {}

        # Determine the number of threads to use
        num_threads = os.cpu_count() or 1
        chunk_size = max(1, len(firing_rule_selectors) // num_threads)

        # Split the indices of the rules into chunks
        chunks = [
            firing_rule_selectors[i : i + chunk_size]
            for i in range(0, len(firing_rule_selectors), chunk_size)
        ]

        with concurrent.futures.ProcessPoolExecutor(
            max_workers=num_threads
        ) as executor:
            futures: list[
                concurrent.futures.Future[
                    tuple[FRONT_STATUS, Evaluation, State, BaseAction]
                ]
            ] = []
            for chunk in chunks:
                for rule_selector in chunk:
                    futures.append(
                        executor.submit(
                            store.tryAction,
                            RemoveRuleAction(
                                RemoveRuleActionParamsType(rule=rule_selector)
                            ),
                        )
                    )

            for future in concurrent.futures.as_completed(futures):
                try:
                    status, evaluation, new_state, action = future.result()
                    # TODO Fix Type
                    evaluations[action.params["rule"]] = evaluation  # type: ignore
                except Exception as e:
                    print_l1(f"Error in future: {e}")
                    continue

        return evaluations
