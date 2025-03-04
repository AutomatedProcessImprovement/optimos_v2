import math

import pytest

from o2.agents.simulated_annealing_agent import SimulatedAnnealingAgent
from o2.models.settings import AgentType
from o2.optimizer import Optimizer
from o2.store import Store
from tests.fixtures.test_helpers import create_mock_solution


def test_simulated_annealing(one_task_store: Store):
    store = one_task_store

    store.settings.agent = AgentType.SIMULATED_ANNEALING
    store.settings.sa_initial_temperature = 5_000_000_000
    store.settings.sa_cooling_factor = 0.90

    optimizer = Optimizer(store)
    optimizer.solve()


def test_auto_cooling_factor(one_task_store: Store):
    store = one_task_store

    store.settings.agent = AgentType.SIMULATED_ANNEALING
    store.settings.sa_initial_temperature = "auto"
    store.settings.sa_cooling_factor = "auto"
    store.settings.sa_cooling_iteration_percent = 0.80
    store.settings.error_radius_in_percent = 0.05
    store.settings.max_iterations = 1000

    store.solution = create_mock_solution(store.current_state, 100, 100)
    store.pareto_fronts[0].solutions[0] = store.solution

    optimizer = Optimizer(store)

    assert optimizer.store.solution.pareto_x == 100
    assert optimizer.store.solution.pareto_y == 100

    assert isinstance(optimizer.agent, SimulatedAnnealingAgent)

    # The temperature should be 4 times the distance of the base solution to the origin
    assert (
        optimizer.agent.temperature
        == 4 * math.sqrt(100**2 + 100**2)
        == pytest.approx(4 * 141.42135624)
    )

    # Type checks
    assert isinstance(optimizer.agent.temperature, float)
    assert isinstance(optimizer.agent.store.settings.sa_cooling_factor, float)

    # The cooling goal is to reach 5% of the distance of the base solution to the origin
    # which is sqrt(100**2 + 100**2 ) * 0.05 = 7.07106781
    # It should be reached after 0.8 * 1000 = 800 iterations
    assert optimizer.agent.temperature * (
        optimizer.agent.store.settings.sa_cooling_factor**800
    ) == pytest.approx(7.07106781)

    # The cooling factor is (7.07/4*141.4)^(1/800) = 0.994...
    assert optimizer.agent.store.settings.sa_cooling_factor == pytest.approx(
        0.994537441038871
    )
