# Initialize the PPO agent
import json
import warnings
from datetime import datetime
from math import ceil
from xml.etree import ElementTree

import gymnasium as gym
from sb3_contrib import MaskablePPO
from stable_baselines3.common.callbacks import CheckpointCallback

from o2.models.constraints import ConstraintsType
from o2.models.state import State
from o2.models.timetable import TimetableType
from o2.ppo_utils.ppo_env import PPOEnv
from o2.store import Store

warnings.filterwarnings(
    "ignore",
    message=".*get variables from other wrappers is deprecated.*",
    category=UserWarning,
)


def main() -> None:
    timetable_path = "examples/demo_legacy/timetable.json"
    constraints_path = "examples/demo_legacy/constraints.json"
    bpmn_path = "examples/demo_legacy/model.bpmn"

    with open(timetable_path) as f:
        timetable = TimetableType.from_dict(json.load(f))

    with open(constraints_path) as f:
        constraints = ConstraintsType.from_dict(json.load(f))

    with open(bpmn_path) as f:
        bpmn_definition = f.read()

    initial_state = State(
        bpmn_definition=bpmn_definition,
        timetable=timetable,
    )
    store = Store.from_state_and_constraints(
        initial_state,
        constraints,
    )

    store.settings.never_select_new_base_solution = True

    STEPS_PER_ITERATION = 50

    env: gym.Env = PPOEnv(store, max_steps=STEPS_PER_ITERATION)
    model = MaskablePPO(
        "MultiInputPolicy",
        env,
        verbose=1,
        # tensorboard_log="./logs/progress_tensorboard/",
        clip_range=0.2,
        # TODO make learning rate smarter
        # learning_rate=linear_schedule(3e-4),
        n_steps=1 * STEPS_PER_ITERATION,  #  Multiple of 50
        batch_size=round(0.5 * STEPS_PER_ITERATION),  # Divisor of 50
        gamma=1,
    )  # type: ignore

    print("Created model & environment")
    print("Input space:", env.observation_space)
    print("Output space:", env.action_space)
    print("Action mask Shape:", env.action_masks().shape)  # type: ignore

    # Train the agent, 100 Iterations
    checkpoint_callback = CheckpointCallback(
        save_freq=500,
        save_path="./model_checkpoints/",
        save_replay_buffer=True,
        save_vecnormalize=True,
    )

    model.learn(total_timesteps=150 * 100, callback=checkpoint_callback)

    # Save the agent
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    model.save(f"models/ppo_maskable-{timestamp}")


if __name__ == "__main__":
    main()
