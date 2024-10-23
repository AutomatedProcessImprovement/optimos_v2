from typing import Any, Dict, Optional, Tuple

import numpy as np
from gym import Env, Space, spaces

from o2.actions.base_action import BaseAction
from o2.models.solution import Solution
from o2.pareto_front import FRONT_STATUS
from o2.ppo_utils.ppo_input import PPOInput
from o2.store import Store

StateType = Dict[str, Space]


class PPOEnv(Env[StateType, int]):
    """The Environment for the PPO algorithm.

    Centered around the Store object, which contains the current state of the
    optimization problem.
    """

    def __init__(self, initial_store: Store) -> None:
        super().__init__()

        self.store = initial_store

        self.actions = PPOInput.get_actions_from_store(self.store)
        self.action_space = PPOInput.get_action_space_from_actions(self.actions)
        self.observation_space = PPOInput.get_observation_space(self.store)
        self.state = PPOInput.state_from_store(self.store)

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[dict] = None,
    ) -> Tuple[StateType, dict]:
        self.store = Store.from_state_and_constraints(
            self.store.base_state, self.store.constraints
        )
        self.state = PPOInput.state_from_store(self.store)
        return self.state, {}

    def step(self, action: int) -> Tuple[StateType, float, bool, bool, dict]:
        action_obj = self.actions[action]
        if action_obj is None:
            return self.state, 0, False, True, {}

        reward: float = 0

        new_solution = Solution.from_parent(self.store.solution, action_obj)
        chosen_tries, not_chosen_tries = self.store.process_many_solutions(
            [new_solution]
        )

        # TODO Improve scores based on how good/bad the solution is
        if not_chosen_tries:
            # TODO Make sure an invalid action / exception reaches this point
            reward = -10
        elif chosen_tries[0][0] == FRONT_STATUS.IN_FRONT:
            reward = 1
        elif chosen_tries[0][0] == FRONT_STATUS.IS_DOMINATED:
            reward = 10
        else:
            reward = 0

        done = False
        truncated = False
        info = {}

        self.actions = PPOInput.get_actions_from_store(self.store)
        self.action_space = PPOInput.get_action_space_from_actions(self.actions)
        self.observation_space = PPOInput.get_observation_space(self.store)
        self.state = PPOInput.state_from_store(self.store)

        return self.state, reward, done, truncated, info

    def action_masks(self) -> np.ndarray:
        """Get the action mask for the current set of actions."""
        return PPOInput.get_action_mask_from_actions(self.actions)

    def render(self, mode="human"):
        pass
