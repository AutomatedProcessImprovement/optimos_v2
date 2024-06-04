# Basic Test Suite to test that the fixture is working correctly
import pytest

from o2.simulation_runner import SimulationRunner
from o2.types.state import State

def test_simulation_runner(simple_state: State):
    log,stats =  SimulationRunner.run_simulation(simple_state)
    # We check that the log size is "plausible"
    assert len(log) > 50 

    
