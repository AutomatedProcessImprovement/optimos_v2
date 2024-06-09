import json
from o2.types.timetable import TimetableType
from o2.simulation_runner import SimulationRunner
from o2.types.constraints import ConstraintsType
import o2.store
import o2.hill_climber
import os
import random
import xml.etree.ElementTree as ET


def main():
    timetable_path = "examples/purchase_timetable.json"
    constraints_path = "examples/purchase_constraints.json"
    bpmn_path = "examples/purchase.bpmn"

    with open(timetable_path, "r") as f:
        timetable = TimetableType.from_dict(json.load(f))

    with open(constraints_path, "r") as f:
        constraints = ConstraintsType.from_dict(json.load(f))

    with open(bpmn_path, "r") as f:
        bpmn_definition = f.read()

    bpmn_tree = ET.parse(bpmn_path)

    initial_state = o2.store.State(
        bpmn_definition=bpmn_definition,
        bpmn_tree=bpmn_tree,
        timetable=timetable,
    )
    store = o2.store.Store(
        state=initial_state,
        constraints=constraints,
    )
    hill_climber = o2.hill_climber.HillClimber(store)
    hill_climber.solve()
    # SimulationRunner.run_simulation(store.state)


if __name__ == "__main__":
    main()
