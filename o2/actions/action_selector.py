import concurrent.futures
import os
import random
from typing import Dict, Optional, Union
from o2.actions.base_action import BaseAction
from o2.actions.modify_size_rule_action import (
    ModifySizeRuleAction,
    ModifySizeRuleActionParamsType,
)
from o2.actions.remove_rule_action import RemoveRuleAction, RemoveRuleActionParamsType
from o2.types.timetable import BatchingRule
from o2.types.evaluation import Evaluation
from o2.pareto_front import FRONT_STATUS

from o2.store import Store
from o2.types.state import State


class ActionSelector:
    @staticmethod
    def select_action(store: Store) -> Optional[BaseAction]:
        tries = 0
        action: Optional[BaseAction] = None
        while action is None:
            if tries > 10:
                return None

            most_impactful_rule_or_action = (
                ActionSelector.find_most_impactful_batching_rule(store)
            )

            if most_impactful_rule_or_action is None:
                return None

            if isinstance(most_impactful_rule_or_action, BaseAction):
                return most_impactful_rule_or_action

            constraint = store.constraints.get_batching_constraints_for_task(
                most_impactful_rule_or_action.task_id
            )
            if constraint is None or len(constraint) == 0:
                print(
                    "\t> TODO: No Constraint set and getting the fn from the rule is not implemented yet"
                )
                return None

            action = ModifySizeRuleAction(
                ModifySizeRuleActionParamsType(
                    rule_hash=most_impactful_rule_or_action.id(),
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
    def find_most_impactful_batching_rule(
        store: "Store",
    ) -> Union[BatchingRule, None]:
        batching_rules = store.state.timetable.batch_processing
        tabu_indices = [action.params["rule_hash"] for action in store.tabu_list]  # type: ignore TODO FIX Type

        # Only allow rules, that can be decreased / modified in size
        batching_rules = [
            rule
            for i, rule in enumerate(batching_rules)
            if rule.can_be_modified(store, -1) and rule.id() not in tabu_indices
        ]

        if len(batching_rules) == 0:
            return None

        base_line_waiting_time = store.current_fastest_evaluation.total_waiting_time

        evaluations: dict[str, Evaluation] = {}

        # Determine the number of threads to use
        num_threads = os.cpu_count() or 1
        chunk_size = max(1, len(batching_rules) // num_threads)

        # Split the indices of the rules into chunks
        chunks = [
            batching_rules[i : i + chunk_size]
            for i in range(0, len(batching_rules), chunk_size)
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
                for rule in chunk:
                    futures.append(
                        executor.submit(
                            store.tryAction,
                            RemoveRuleAction(
                                RemoveRuleActionParamsType(rule_hash=rule.id())
                            ),
                        )
                    )

            for future in concurrent.futures.as_completed(futures):
                try:
                    status, evaluation, new_state, action = future.result()
                    evaluations[action.params["rule_hash"]] = evaluation  # type: ignore TODO Fix Type
                except Exception as e:
                    print(f"\t> Error in future: {e}")
                    continue

        # Find the rule that has the most impact
        most_impactful_rule_hash = max(
            evaluations,
            key=lambda rule_hash: evaluations[rule_hash].total_waiting_time,
        )
        # most_impactful_evaluation = evaluations[most_impactful_rule_hash]

        # # TODO: This needs to move to a better place
        # if (
        #     store.current_pareto_front.is_in_front(most_impactful_evaluation)
        #     == FRONT_STATUS.IS_DOMINATED
        # ):
        #     print(
        #         f"\t> Most impactful rule dominates current pareto front. Rule: {most_impactful_rule_hash}"
        #     )
        #     return RemoveRuleAction(
        #         RemoveRuleActionParamsType(rule_hash=most_impactful_rule_hash)
        #     )

        most_impactful_rule = next(
            (rule for rule in batching_rules if rule.id() == most_impactful_rule_hash),
            None,
        )
        print("\t> Found most impactful rule: ", most_impactful_rule_hash)

        return most_impactful_rule
