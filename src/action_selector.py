import random
from typing import Optional
from src.actions import Action, RemoveRuleAction
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

            batching_rules = store.state.timetable.batch_processing
            if len(batching_rules) == 0:
                return None
            random_index = random.randint(0, len(batching_rules) - 1)
            action = RemoveRuleAction({"rule_index": random_index})

            if action in store.tabu_list:
                action = None
                tries += 1
                continue

            return action
