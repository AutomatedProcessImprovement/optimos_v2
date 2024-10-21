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
    def __init__(self, initial_store: Store) -> None:
        super().__init__()

        self.store = initial_store

        self.action_space = PPOInput.action_space_from_store(self.store)
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
        action_obj = self.base_action_from_index(action)

        reward: float = 0

        new_solution = Solution.from_parent(self.store.solution, action_obj)
        status, solution = self.store.try_solution(new_solution)
        # TODO Improve scores based on how good/bad the solution is
        if status == FRONT_STATUS.INVALID:
            # TODO Make sure an invalid action / exception reaches this point
            reward = -10
        elif status == FRONT_STATUS.IN_FRONT:
            reward = 1
        elif status == FRONT_STATUS.IS_DOMINATED:
            reward = 10
        else:
            reward = 0

        done = False
        truncated = False
        info = {}

        self.action_space = PPOInput.action_space_from_store(self.store)
        self.observation_space = PPOInput.get_observation_space(self.store)
        self.state = PPOInput.state_from_store(self.store)

        return self.state, reward, done, truncated, info

    def base_action_from_index(self, action_index: int) -> BaseAction:
        raise NotImplementedError()

    def action_masks(self):
        # Return a mask indicating which actions are valid
        # TODO: We can just get the validity of actions after creating them,
        # and running the validiy check
        pass

    def render(self, mode="human"):
        pass
