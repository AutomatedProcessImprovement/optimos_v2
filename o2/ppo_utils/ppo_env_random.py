from typing import Optional

import numpy as np
from gymnasium import Env, Space, spaces

from o2.models.solution import Solution
from o2.pareto_front import FRONT_STATUS
from o2.ppo_utils.ppo_input import PPOInput
from o2.store import Store
from o2.util.indented_printer import print_l0, print_l1
from o2.util.logger import error

StateType = dict[str, float]


class PPOEnvRandom(Env[StateType, np.int64]):
    """The Environment for the PPO algorithm.

    Centered around the Store object, which contains the current state of the
    optimization problem.
    """

    def __init__(self, initial_store: Store, max_steps=float("inf")) -> None:
        super().__init__()

        self.store = initial_store
        self.max_steps = max_steps

        self.actions = PPOInput.get_actions_from_store(self.store)
        self.action_space = PPOInput.get_action_space_from_actions(self.actions)
        self.observation_space = spaces.Dict(
            {
                "random": spaces.Box(low=0, high=1, shape=(1, 1)),
            }
        )
        self.state = {"random": np.random.random()}
        self.stepCount = 0
        self.iteration = 0

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[dict] = None,
    ) -> tuple[StateType, dict]:
        super().reset(seed=seed)
        self.stepCount = 0
        self.iteration += 1
        self.store = Store(self.store.base_solution, self.store.constraints)
        self.actions = PPOInput.get_actions_from_store(self.store)
        self.state = {"random": np.random.random()}
        self.action_space = PPOInput.get_action_space_from_actions(self.actions)
        self.observation_space = spaces.Dict(
            {
                "random": spaces.Box(low=0, high=1, shape=(1, 1)),
            }
        )
        return self.state, {}

    def step(self, action: np.int64) -> tuple[StateType, float, bool, bool, dict]:
        # As we are reimplementing PPO in parts, the step function is actually not needed.
        # So we raise an exception to avoid using it.
        raise Exception("PPOEnvRandom does not support step")

    def action_masks(self) -> np.ndarray:
        """Get the action mask for the current set of actions."""
        # As we are reimplementing PPO in parts, the action_masks function is actually not needed.
        # So we raise an exception to avoid using it.
        raise Exception("PPOEnvRandom does not support action_masks")

    def render(self, mode="human"):
        pass
