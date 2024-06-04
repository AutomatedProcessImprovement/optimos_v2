# Basic Test Suite to test that the fixture is working correctly
import pytest

from o2.simulation_runner import SimulationRunner
from o2.types.state import State

def test_simulation_runner(state: State):
    log,stats =  SimulationRunner.run_simulation(state)
    assert log is not None

    
