import json
import warnings
from datetime import datetime
from math import ceil
from xml.etree import ElementTree

import gymnasium as gym
from sb3_contrib import MaskablePPO
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.env_checker import check_env

from o2.models.constraints import ConstraintsType
from o2.models.state import State
from o2.models.timetable import TimetableType
from o2.ppo_utils.ppo_env import PPOEnv
from o2.store import Store


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

    env: gym.Env = PPOEnv(store, max_steps=50)

    check_env(env)
