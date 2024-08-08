# Basic Test Suite to test that the fixture is working correctly
import pytest

from o2.models.state import State
from o2.simulation_runner import SimulationRunner


def test_simulation_runner(simple_state: State):
    global_kpis, task_kpis, resource_kpis, log_info = SimulationRunner.run_simulation(
        simple_state
    )

    # Sanity check
    assert global_kpis.cycle_time.total > 0
