import json
from src.types.timetable import TimetableType
from src.simulation_runner import SimulationRunner
from src.types.constraints import ConstraintsType
import src.store
import src.hill_climber


def main():
    timetable_path = "examples/purchase_timetable.json"
    bpmn_path = "examples/purchase.bpmn"

    with open(timetable_path, "r") as f:
        timetable = TimetableType.from_dict(json.load(f))

    with open(bpmn_path, "r") as f:
        bpmn_definition = f.read()

    initial_state = src.store.State(
        bpmn_definition=bpmn_definition,
        timetable=timetable,
        constraints=ConstraintsType(),
    )
    store = src.store.Store(initial_state)
    hill_climber = src.hill_climber.HillClimber(store)
    hill_climber.solve()
    # SimulationRunner.run_simulation(store.state)


if __name__ == "__main__":
    main()
