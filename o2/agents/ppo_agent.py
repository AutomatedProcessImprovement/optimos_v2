from typing import Optional

import gymnasium as gym
import numpy as np
import torch as th
from gymnasium import spaces
from numpy import ndarray
from sb3_contrib import MaskablePPO
from sb3_contrib.common.maskable.utils import get_action_masks
from stable_baselines3.common.utils import obs_as_tensor

from o2.actions.base_actions.base_action import BaseAction
from o2.agents.agent import Agent, NoActionsLeftError
from o2.agents.tabu_agent import TabuAgent
from o2.models.solution import Solution
from o2.pareto_front import FRONT_STATUS
from o2.ppo_utils.ppo_env import PPOEnv
from o2.ppo_utils.ppo_input import PPOInput
from o2.store import SolutionTry, Store
from o2.util.indented_printer import print_l1, print_l2


class PPOAgent(Agent):
    """Selects the best action to take next, based on the current state of the store."""

    def __init__(self, store: Store) -> None:
        super().__init__(store)
        if store.settings.ppo_use_existing_model:
            self.model = MaskablePPO.load(store.settings.ppo_model_path)
        else:
            env: gym.Env = PPOEnv(
                store, max_steps=store.settings.ppo_steps_per_iteration
            )
            self.model = MaskablePPO(
                "MultiInputPolicy",
                env,
                verbose=1,
                # tensorboard_log="./logs/progress_tensorboard/",
                clip_range=0.2,
                # TODO make learning rate smarter
                # learning_rate=linear_schedule(3e-4),
                n_steps=1 * store.settings.ppo_steps_per_iteration,  #  Multiple of 50
                batch_size=round(
                    0.5 * store.settings.ppo_steps_per_iteration
                ),  # Divsior of 50
                gamma=1,
            )

            self.model._setup_learn(
                store.settings.max_iterations,
                callback=None,
                reset_num_timesteps=True,
                tb_log_name="PPO",
                progress_bar=False,
            )
            self.last_actions: ndarray
            self.last_values: ndarray
            self.log_probs: ndarray
            self.last_action_mask: ndarray

    def select_actions(self, store: Store) -> Optional[list[BaseAction]]:
        """Select the best actions to take next.

        It will pick at most cpu_count actions, so parallel evaluation is possible.

        If the possible options for the current base evaluation are exhausted,
        it will choose a new base evaluation.
        """
        state = PPOInput.get_state_from_store(store)
        action_from_store = PPOInput.get_actions_from_store(store)
        action_count = len([a for a in action_from_store if a is not None])
        if action_count == 0:
            # TODO: We need to reset the env here
            raise NoActionsLeftError()
        else:
            print_l1(f"Choosing best action out of {action_count} possible actions.")
        action_mask = PPOInput.get_action_mask_from_actions(action_from_store)
        self.last_action_mask = action_mask

        # Collect a single step
        with th.no_grad():
            obs_tensor = obs_as_tensor(self.model._last_obs, self.model.device)  # type: ignore
            actions, values, log_probs = self.model.policy(
                obs_tensor, action_masks=action_mask
            )
            self.last_actions = actions
            self.last_values = values
            self.log_probs = log_probs

        [action_index] = actions.cpu().numpy()

        if action_index is None:
            raise ValueError("Model did not return an action index.")
        action = action_from_store[action_index]
        if action is None:
            return None
        return [action]

    def select_new_base_solution(
        self, proposed_solution_try: Optional[SolutionTry] = None
    ) -> Solution:
        """Select a new base solution."""
        return TabuAgent(self.store).select_new_base_solution(proposed_solution_try)

    def result_callback(
        self, chosen_tries: list[SolutionTry], not_chosen_tries: list[SolutionTry]
    ) -> None:
        """Call to handle the result of the evaluation."""

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
        self.observation_space = PPOInput.get_observation_space(self.store)
        self.state = PPOInput.get_state_from_store(self.store)

        print_l1(f"Done. Reward: {reward}")
        action_count = len([a for a in self.actions if a is not None])
        if action_count == 0:
            print_l1("No actions available for next step")
            done = True
        else:
            print_l1(f"{action_count} actions available for next step")

        return self.state, reward, done
