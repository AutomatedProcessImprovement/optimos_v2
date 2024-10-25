from typing import Any, Dict, Optional, Tuple
import warnings

import numpy as np
from gymnasium import Env, Space

from o2.actions.base_action import BaseAction
from o2.models.evaluation import Evaluation
from o2.models.solution import Solution
from o2.pareto_front import FRONT_STATUS
from o2.ppo_utils.ppo_input import PPOInput
from o2.store import Store
from o2.util.indented_printer import print_l0, print_l1

StateType = Dict[str, Space]


class PPOEnv(Env[StateType, np.int64]):
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
        self.observation_space = PPOInput.get_observation_space(self.store)
        self.state = PPOInput.get_state_from_store(self.store)
        self.stepCount = 0
        self.iteration = 0

    def reset(
        self,
        *,
        seed: Optional[int] = None,
        options: Optional[dict] = None,
    ) -> Tuple[StateType, dict]:
        super().reset(seed=seed)
        self.stepCount = 0
        self.iteration += 1
        self.store = Store(self.store.base_solution, self.store.constraints)
        self.actions = PPOInput.get_actions_from_store(self.store)
        self.state = PPOInput.get_state_from_store(self.store)
        self.action_space = PPOInput.get_action_space_from_actions(self.actions)
        self.observation_space = PPOInput.get_observation_space(self.store)
        return self.state, {}

    def step(self, action: np.int64) -> Tuple[StateType, float, bool, bool, dict]:
        self.stepCount += 1

        action_obj = self.actions[action]
        print_l0(f"Step {self.stepCount} Iteration {self.iteration}")
        print_l1(f"Action #{action}: {action_obj}")
        if action_obj is None:
            return self.state, 0, False, True, {}

        reward: float = 0

        try:
            new_solution = Solution.from_parent(self.store.solution, action_obj)
        except Exception as e:
            print("Error in action:", e)
            self.store.mark_action_as_tabu(action_obj)
            return self.state, -1, False, False, {}
        chosen_tries, not_chosen_tries = self.store.process_many_solutions(
            [new_solution], None
        )

        # TODO Improve scores based on how good/bad the solution is
        if not_chosen_tries:
            # TODO Make sure an invalid action / exception reaches this point
            reward = -1
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
        self.state = PPOInput.get_state_from_store(self.store)

        print_l1(f"Done. Reward: {reward}")
        action_count = len([a for a in self.actions if a is not None])
        if action_count == 0:
            print_l1("No actions available for next step")
            done = True
        else:
            print_l1(f"{action_count} actions available for next step")

        if self.stepCount >= self.max_steps:
            print_l1("Max steps reached")
            done = True

        return self.state, reward, done, truncated, info

    def action_masks(self) -> np.ndarray:
        """Get the action mask for the current set of actions."""
        return PPOInput.get_action_mask_from_actions(self.actions)

    def render(self, mode="human"):
        pass
