import json

from prosimos.simulation_engine import SimDiffSetup, run_simpy_simulation

from o2.models.state import State
from o2.models.timetable import TimetableType
from o2.util.sim_diff_setup_fileless import SimDiffSetupFileless
from o2_evaluation.data_collector import store_with_baseline_constraints

timetable_path = "o2_evaluation/scenarios/bpi_challenge_2017/bpi_challenge_2017_with_batching.json"
bpmn_path = "o2_evaluation/scenarios/bpi_challenge_2017/bpi_challenge_2017.bpmn"

# with open(timetable_path) as f:
#     timetable = TimetableType.from_dict(json.load(f))
#     print(timetable.to_json())


# store = store_with_baseline_constraints(timetable_path, bpmn_path)

# print(store.base_evaluation.is_empty)
# setup = SimDiffSetup(bpmn_path, timetable_path, False, 100)
with open(bpmn_path) as bpmn_file:
    bpmn = bpmn_file.read()

with open(timetable_path) as timetable_file:
    timetable = TimetableType.from_dict(json.load(timetable_file))


state = State(bpmn, timetable, for_testing=False)
setup = state.to_sim_diff_setup()

# print(
#     state.bpmn_definition,
#     state.timetable,
#     state.timetable.total_cases,
# )

setup = SimDiffSetupFileless("test", state.bpmn_definition, state.timetable, False, 1000)

run_simpy_simulation(setup, None, None)
