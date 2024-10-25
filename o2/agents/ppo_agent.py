from typing import Optional

from o2.actions.base_action import BaseAction
from o2.agents.agent import Agent
from o2.store import Store


class PPOAgent(Agent):
    """Selects the best action to take next, based on the current state of the store."""

    def select_actions(self, store: Store) -> Optional[list[BaseAction]]:
        """Select the best actions to take next.

        It will pick at most cpu_count actions, so parallel evaluation is possible.

        If the possible options for the current base evaluation are exhausted,
        it will choose a new base evaluation.
        """

        # TODO: Load pretrained model, and use it to select actions
        raise NotImplementedError
