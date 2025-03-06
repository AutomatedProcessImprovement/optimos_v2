import os
from typing import TYPE_CHECKING, Optional

from o2.agents.ppo_agent import PPOAgent

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

import gymnasium as gym
import numpy as np
import torch as th
from gymnasium import spaces
from stable_baselines3.common.utils import obs_as_tensor

from o2.actions.base_actions.base_action import BaseAction
from o2.agents.agent import Agent, NoActionsLeftError
from o2.agents.tabu_agent import TabuAgent
from o2.models.solution import Solution
from o2.pareto_front import FRONT_STATUS
from o2.ppo_utils.ppo_env import PPOEnv
from o2.ppo_utils.ppo_input import PPOInput
from o2.store import SolutionTry, Store
from o2.util.indented_printer import print_l1

if TYPE_CHECKING:
    from numpy import ndarray


class PPOAgentRandom(PPOAgent):
    """Selects the best action to take next, based on the current state of the store."""

    def result_callback(
        self, chosen_tries: list[SolutionTry], not_chosen_tries: list[SolutionTry]
    ) -> None:
        """Handle the result of the evaluation."""
        result = chosen_tries[0] if chosen_tries else not_chosen_tries[0]

        new_obs, reward, done = self.step_info_from_try(result)
        rewards = [reward]
        dones = np.array([1 if done else 0])
        actions = self.last_actions.reshape(-1, 1)
        log_probs = self.log_probs
        action_masks = self.last_action_mask

        # Add collected data to the rollout buffer
        self.model.rollout_buffer.add(
            self.model._last_obs,
            actions,
            rewards,
            self.model._last_episode_starts or dones,
            self.last_values,
            log_probs,
            action_masks=action_masks,
        )
        self.model._last_obs = new_obs
        self.model._last_episode_starts = dones  # type: ignore

        # Train if the buffer is full
        if self.model.rollout_buffer.full:
            print_l1("Rollout buffer full, training...")
            with th.no_grad():
                last_values = self.model.policy.predict_values(
                    obs_as_tensor(new_obs, self.model.device)
                )
            self.model.rollout_buffer.compute_returns_and_advantage(
                last_values=last_values,
                dones=dones,  # type: ignore
            )
            self.model.train()
            self.model.rollout_buffer.reset()

        # If the episode is done, select a new base solution
        if dones[0]:
            tmp_agent = TabuAgent(self.store)
            while True:
                self.store.solution = tmp_agent._select_new_base_evaluation(
                    reinsert_current_solution=False
                )
                actions = PPOInput.get_actions_from_store(self.store)
                action_count = len([a for a in actions if a is not None])
                if action_count > 0:
                    break
                else:
                    print_l1(
                        "Still no actions available for next step, selecting new base solution again."
                    )

    def step_info_from_try(self, solution_try: SolutionTry) -> tuple[dict, float, bool]:
        """Get the step info from the given SolutionTry."""
        # TODO Improve scores based on how good/bad the solution is
        status, solution = solution_try
        if status == FRONT_STATUS.INVALID:
            reward = -1
        elif status == FRONT_STATUS.IN_FRONT:
            reward = 1
        elif status == FRONT_STATUS.IS_DOMINATED:
            reward = 10
        else:
            reward = -1

        done = False

        self.actions = PPOInput.get_actions_from_store(self.store)
        self.action_space = PPOInput.get_action_space_from_actions(self.actions)
        self.observation_space = spaces.Dict()
        self.state = {}

        print_l1(f"Done. Reward: {reward}")
        action_count = len([a for a in self.actions if a is not None])
        if action_count == 0:
            print_l1("No actions available for next step")
            done = True
        else:
            print_l1(f"{action_count} actions available for next step")

        return self.state, reward, done
