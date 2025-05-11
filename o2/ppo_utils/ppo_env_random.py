from typing import Optional

import numpy as np
from gymnasium import Env, spaces

from o2.ppo_utils.ppo_input import PPOInput
from o2.store import Store

StateType = dict[str, float]


class PPOEnvRandom(Env[StateType, np.int64]):
    """The Environment for the PPO algorithm.

    Centered around the Store object, which contains the current state of the
    optimization problem.
    """

    def __init__(self, initial_store: Store, max_steps: float = float("inf")) -> None:
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
        """Reset the environment to its initial state.

        Increments the iteration counter and reinitializes the store and state
        for random action selection.
        """
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
        """Take an action in the environment.

        Not implemented in this random environment as we use custom PPO implementation.
        """
        # As we are reimplementing PPO in parts, the step function is actually not needed.
        # So we raise an exception to avoid using it.
        raise Exception("PPOEnvRandom does not support step")

    def action_masks(self) -> np.ndarray:
        """Get the action mask for the current set of actions."""
        # As we are reimplementing PPO in parts, the action_masks function is actually not needed.
        # So we raise an exception to avoid using it.
        raise Exception("PPOEnvRandom does not support action_masks")

    def render(self, mode: str = "human") -> None:
        """Render the current state of the environment.

        Not implemented for this random environment.
        """
        pass
