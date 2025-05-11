import os

from typing_extensions import override

from o2.agents.ppo_agent import PPOAgent
from o2.ppo_utils.ppo_env_random import PPOEnvRandom

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import gymnasium as gym
import numpy as np
from gymnasium import spaces

from o2.ppo_utils.ppo_input import PPOInput
from o2.store import Store


class PPOAgentRandom(PPOAgent):
    """Selects the best action to take next, based on the current state of the store."""

    def __init__(self, store: Store) -> None:
        super().__init__(store)

        self.store.settings.disable_action_validity_check = True

    @override
    def get_env(self) -> gym.Env:
        """Get the environment for the PPO agent."""
        return PPOEnvRandom(self.store, max_steps=self.store.settings.ppo_steps_per_iteration)

    @override
    def update_state(self) -> None:
        """Update the state of the agent."""
        self.actions = PPOInput.get_actions_from_store(self.store)
        self.action_space = PPOInput.get_action_space_from_actions(self.actions)
        self.observation_space = spaces.Dict(
            {
                "random": spaces.Box(low=0, high=1, shape=(1, 1)),
            }
        )
        self.state = {"random": np.array([[np.random.random()]])}
