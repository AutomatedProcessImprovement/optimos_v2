# Initialize the PPO agent
from datetime import datetime
import json
from xml.etree import ElementTree

import gym
from sb3_contrib import MaskablePPO
from stable_baselines3 import PPO

from o2.models.constraints import ConstraintsType
from o2.models.state import State
from o2.models.timetable import TimetableType
from o2.ppo_utils.ppo_env import PPOEnv
from o2.store import Store


def main():
    timetable_path = "examples/demo_legacy/timetable.json"
    constraints_path = "examples/demo_legacy/constraints.json"
    bpmn_path = "examples/demo_legacy/model.bpmn"

    with open(timetable_path) as f:
        timetable = TimetableType.from_dict(json.load(f))

    with open(constraints_path) as f:
        constraints = ConstraintsType.from_dict(json.load(f))

    with open(bpmn_path) as f:
        bpmn_definition = f.read()

    bpmn_tree = ElementTree.parse(bpmn_path)

    initial_state = State(
        bpmn_definition=bpmn_definition,
        bpmn_tree=bpmn_tree,
        timetable=timetable,
    )
    store = Store.from_state_and_constraints(
        initial_state,
        constraints,
    )

    env: gym.Env = PPOEnv(store)
    model = MaskablePPO("MlpPolicy", env, verbose=1)  # type: ignore

    # Train the agent
    model.learn(total_timesteps=1000)

    # Save the agent
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    model.save(f"models/ppo_maskable-{timestamp}")


if __name__ == "__main__":
    main()
