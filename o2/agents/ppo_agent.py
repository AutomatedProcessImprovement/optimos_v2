from typing import Optional

from sb3_contrib import MaskablePPO

from o2.actions.base_actions.base_action import BaseAction
from o2.agents.agent import Agent
from o2.agents.tabu_agent import TabuAgent
from o2.models.solution import Solution
from o2.ppo_utils.ppo_input import PPOInput
from o2.store import SolutionTry, Store
from o2.util.indented_printer import print_l1, print_l2


class PPOAgent(Agent):
    """Selects the best action to take next, based on the current state of the store."""

    def __init__(self, store: Store) -> None:
        super().__init__(store)
        self.model = MaskablePPO.load(store.settings.ppo_model_path)

    def select_actions(self, store: Store) -> Optional[list[BaseAction]]:
        """Select the best actions to take next.

        It will pick at most cpu_count actions, so parallel evaluation is possible.

        If the possible options for the current base evaluation are exhausted,
        it will choose a new base evaluation.
        """
        state = PPOInput.get_state_from_store(store)
        actions = PPOInput.get_actions_from_store(store)
        action_count = len([a for a in actions if a is not None])
        if action_count == 0:
            raise ValueError("No actions available.")
        else:
            print_l1(f"Choosing best action out of {action_count} possible actions.")
        action_mask = PPOInput.get_action_mask_from_actions(actions)
        action_index, _ = self.model.predict(state, action_masks=action_mask)
        if action_index is None:
            raise ValueError("Model did not return an action index.")
        action = actions[action_index]
        if action is None:
            return None
        return [action]

    def select_new_base_solution(
        self, proposed_solution_try: Optional[SolutionTry] = None
    ) -> Solution:
        """Select a new base solution."""
        return TabuAgent(self.store).select_new_base_solution(proposed_solution_try)
