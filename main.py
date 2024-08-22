import json
import xml.etree.ElementTree as ElementTree

import o2.hill_climber
import o2.store
from o2.models.constraints import ConstraintsType
from o2.models.timetable import TimetableType


def main():
    timetable_path = "examples/demo_batching/timetable.json"
    constraints_path = "examples/demo_batching/constraints.json"
    bpmn_path = "examples/demo_batching/model.bpmn"

    # timetable_path = "examples/demo_legacy/timetable.json"
    # constraints_path = "examples/demo_legacy/constraints.json"
    # bpmn_path = "examples/demo_legacy/model.bpmn"

    # timetable_path = "examples/purchase_timetable.json"
    # constraints_path = "examples/purchase_constraints.json"
    # bpmn_path = "examples/purchase.bpmn"

    with open(timetable_path, "r") as f:
        timetable = TimetableType.from_dict(json.load(f))

    with open(constraints_path, "r") as f:
        constraints = ConstraintsType.from_dict(json.load(f))

    with open(bpmn_path, "r") as f:
        bpmn_definition = f.read()

    bpmn_tree = ElementTree.parse(bpmn_path)

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
