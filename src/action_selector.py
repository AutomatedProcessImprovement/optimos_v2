import concurrent.futures
import os
import random
from typing import Dict, Optional
from src.types.evaluation import Evaluation
from src.pareto_front import FRONT_STATUS
from src.actions import (
    Action,
    ModifySizeRuleAction,
    ModifySizeRuleActionParamsType,
    RemoveRuleAction,
)
from src.store import Store
from src.types.state import State


class ActionSelector:
    @staticmethod
    def select_action(store: Store) -> Optional[Action]:
        tries = 0
        action: Optional[Action] = None
        while action is None:

            if tries > 100:
                return None

            most_impactful_rule = ActionSelector.find_most_impactful_batching_rule(
                store
            )

            if most_impactful_rule is None:
                return None

            rule = store.state.timetable.batch_processing[most_impactful_rule]
            constraint = store.constraints.get_batching_constraints_for_task(
                rule.task_id
            )
            if constraint is None or len(constraint) == 0:
                print(
                    "\t> TODO: No Constraint set and getting the fn from the rule is not implemented yet"
                )
                return None

            action = ModifySizeRuleAction(
                ModifySizeRuleActionParamsType(
                    rule_index=most_impactful_rule,
                    size_increment=-1,
                    duration_fn=constraint[0].duration_fn,
                )
            )
            if action in store.tabu_list:
                print(
                    f"\t> Action is tabu list, trying again... ({tries}/100): {action}"
                )
                action = None
                tries += 1
                continue

            return action

            # batching_rules = store.state.timetable.batch_processing
            # if len(batching_rules) == 0:
            #     return None
            # random_index = random.randint(0, len(batching_rules) - 1)
            # action = RemoveRuleAction({"rule_index": random_index})

            # return action

    # Tries to remove all batching rules and returns the one that has the most impact
    # This runs multithreaded.
    @staticmethod
    def find_most_impactful_batching_rule(store: "Store") -> Optional[int]:
        batching_rules = store.state.timetable.batch_processing
        tabu_indices = [action.params["rule_index"] for action in store.tabu_list]

        # Only allow rules, that can be decreased / modified in size
        batching_rules = [
            rule
            for i, rule in enumerate(batching_rules)
            if rule.can_be_modified(store, -1) and i not in tabu_indices
        ]

        if len(batching_rules) == 0:
            return None

        base_line_waiting_time = store.current_fastest_evaluation.total_waiting_time
        change_in_waiting_time = {}

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
                    tuple[FRONT_STATUS, Evaluation, State, Action]
                ]
            ] = []
            for chunk in chunks:
                for rule in chunk:
                    index = batching_rules.index(rule)
                    futures.append(
                        executor.submit(
                            store.tryAction, RemoveRuleAction({"rule_index": index})
                        )
                    )

            for future in concurrent.futures.as_completed(futures):
                try:
                    status, evaluation, new_state, action = future.result()
                    change_in_waiting_time[action.params["rule_index"]] = (
                        base_line_waiting_time - evaluation.total_waiting_time
                    )
                except Exception as e:
                    print(f"\t>Error in future: {e}")
                    continue

        # Find the rule that has the most impact
        most_impactful_rule = max(
            change_in_waiting_time, key=change_in_waiting_time.get  # type: ignore
        )  # type: ignore

        print("\t> Found most impactful rule: ", most_impactful_rule)
        return most_impactful_rule
