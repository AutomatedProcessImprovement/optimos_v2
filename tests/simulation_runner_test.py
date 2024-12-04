# Basic Test Suite to test that the fixture is working correctly
import pytest

from o2.models.evaluation import Evaluation
from o2.models.state import State
from o2.simulation_runner import SimulationRunner


def test_simulation_runner(simple_state: State):
    result = SimulationRunner.run_simulation(
        simple_state,
        show_simulation_errors=True,
    )

    evaluation = Evaluation.from_run_simulation_result(
        simple_state.timetable.get_hourly_rates(),
        simple_state.timetable.get_fixed_cost_fns(),
        simple_state.timetable.batching_rules_exist,
        result,
    )

    # Sanity checks
    assert evaluation.total_duration > 0
    assert evaluation.total_cost > 0
    assert evaluation.total_waiting_time > 0
