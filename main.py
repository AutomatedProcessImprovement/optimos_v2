import json
import xml.etree.ElementTree as ElementTree

import o2.hill_climber
from o2.models.settings import AgentType
import o2.store
from o2.models.constraints import ConstraintsType
from o2.models.timetable import TimetableType


def main():
    # timetable_path = "examples/demo_batching/timetable.json"
    # constraints_path = "examples/demo_batching/constraints.json"
    # bpmn_path = "examples/demo_batching/model.bpmn"

    timetable_path = "examples/demo_legacy/timetable.json"
    constraints_path = "examples/demo_legacy/constraints.json"
    bpmn_path = "examples/demo_legacy/model.bpmn"

    # timetable_path = "examples/purchase_timetable.json"
    # constraints_path = "examples/purchase_constraints.json"
    # bpmn_path = "examples/purchase.bpmn"

    with open(timetable_path, "r") as f:
        timetable = TimetableType.from_dict(json.load(f))

    with open(constraints_path, "r") as f:
        constraints = ConstraintsType.from_dict(json.load(f))

    with open(bpmn_path, "r") as f:
        bpmn_definition = f.read()

    initial_state = o2.store.State(
        bpmn_definition=bpmn_definition,
        timetable=timetable,
    )
    store = o2.store.Store.from_state_and_constraints(
        initial_state,
        constraints,
    )

    # Change settings here:
    # store.settings.[...] = ...

    # Enable legacy mode
    store.settings.optimos_legacy_mode = True
    store.settings.max_iterations = 1000
    store.settings.max_non_improving_actions = 200
    store.settings.sa_initial_temperature = 5_000_000_000
    store.settings.sa_cooling_factor = 0.90
    store.settings.agent = AgentType.SIMULATED_ANNEALING

    hill_climber = o2.hill_climber.HillClimber(store)
    hill_climber.solve()
    # SimulationRunner.run_simulation(store.state)


if __name__ == "__main__":
    main()
