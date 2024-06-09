import concurrent.futures
import os
import random
from typing import Optional, Tuple, Union
from o2.actions.base_action import BaseAction
from o2.actions.modify_size_rule_action import (
    ModifySizeRuleAction,
    ModifySizeRuleActionParamsType,
)
from o2.actions.remove_rule_action import (
    RemoveRuleAction,
    RemoveRuleActionParamsType,
)
from o2.types.timetable import BatchingRule
from o2.types.evaluation import Evaluation
from o2.pareto_front import FRONT_STATUS

from o2.store import Store
from o2.types.state import State
from o2.types.rule_selector import RuleSelector


class ActionSelector:
    @staticmethod
    def select_action(store: Store) -> Optional[BaseAction]:
        tries = 0
        action: Optional[BaseAction] = None
        while action is None:
            if tries > 10:
                return None

            (
                most_impactful_rule_selector,
                most_impactful_evaluation,
            ) = ActionSelector.find_most_impactful_firing_rule(store)

            if most_impactful_rule_selector is None:
                return None

            # Check if this evaluation beats the current pareto front
            if store.current_fastest_evaluation.is_dominated_by(
                most_impactful_evaluation
            ):
                print(
                    f"\t> Most impactful rule dominates current. Rule: {most_impactful_rule_selector}"
                )
                return RemoveRuleAction(
                    RemoveRuleActionParamsType(rule=most_impactful_rule_selector)
                )

            constraint = store.constraints.get_batching_constraints_for_task(
                most_impactful_rule_selector.batching_rule_task_id
            )
            if constraint is None or len(constraint) == 0:
                print(
                    "\t> TODO: No Constraint set and getting the fn from the rule is not implemented yet"
                )
                return None

            action = ModifySizeRuleAction(
                ModifySizeRuleActionParamsType(
                    rule=most_impactful_rule_selector,
                    size_increment=-1,
                    duration_fn=constraint[0].duration_fn,
                )
            )
            if action in store.tabu_list:
                print(
                    f"\t> BaseAction is tabu list, trying again... ({tries}/10): {action}"
                )
                action = None
                tries += 1
                continue

            return action

            # batching_rules = store.state.timetable.batch_processing
            # if len(batching_rules) == 0:
            #     return None
            # random_index = random.randint(0, len(batching_rules) - 1)
            # action = RemoveRuleAction({"rule_hash": random_index})

            # return action

    # Tries to remove all batching rules and returns the one that has the most impact
    # This runs multithreaded.
    @staticmethod
    def find_most_impactful_firing_rule(
        store: "Store",
    ) -> Union[Tuple[RuleSelector, Evaluation], Tuple[None, None]]:
        batching_rules = store.state.timetable.batch_processing
        tabu_indices = [action.params["rule_hash"] for action in store.tabu_list]  # type: ignore TODO FIX Type

        # Only allow rules, that can be decreased / modified in size
        batching_rules = [
            rule
            for i, rule in enumerate(batching_rules)
            if rule.can_be_modified(store, -1) and rule.id() not in tabu_indices
        ]

        firing_rule_selectors = [
            RuleSelector(rule.task_id, (or_index, and_index))
            for rule in batching_rules
            for or_index, or_rule in enumerate(rule.firing_rules)
            for and_index, _ in enumerate(or_rule)
        ]

        if len(batching_rules) == 0:
            return None, None

        base_line_waiting_time = store.current_fastest_evaluation.total_waiting_time

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
                    evaluations[action.params["rule"]] = evaluation  # type: ignore TODO Fix Type
                except Exception as e:
                    print(f"\t> Error in future: {e}")
                    continue

        # Find the rule that has the most impact,
        # aka. the one that, after being removed, has reduced the waiting time the most
        # and therefore has the most potential to improve the current fastest evaluation
        most_impactful_rule_selector = min(
            evaluations,
            key=lambda rule_selector: evaluations[rule_selector].total_waiting_time,
        )
        most_impactful_evaluation = evaluations[most_impactful_rule_selector]

        print("\t> Found most impactful rule: ", most_impactful_rule_selector)
        return (most_impactful_rule_selector, most_impactful_evaluation)
