# Basic Test Suite to test that the fixture is working correctly
import pytest

from o2.models.state import State
from o2.simulation_runner import SimulationRunner
from optimos_v2.o2.models.evaluation import Evaluation


def test_simulation_runner(simple_state: State):
    global_kpis, task_kpis, resource_kpis, log_info = SimulationRunner.run_simulation(
        simple_state
    )

    evaluation = Evaluation(
        global_kpis=global_kpis,
        task_kpis=task_kpis,
        resource_kpis=resource_kpis,
        log_info=log_info,
    )

    # Sanity checks
    assert evaluation.total_cycle_time > 0
    assert evaluation.total_cost > 0
    assert evaluation.total_waiting_time > 0
