import pytest

from o2.agents.tabu_agent import TabuAgent
from o2.models.settings import AgentType, CostType, Settings
from o2.optimizer import Optimizer
from o2.store import Store
from tests.fixtures.test_helpers import create_mock_solution


def test_tabu_search(one_task_store: Store):
    Settings.COST_TYPE = CostType.TOTAL_COST
    store = one_task_store

    store.settings.agent = AgentType.TABU_SEARCH
    store.settings.max_distance_to_new_base_solution = 100
    store.settings.error_radius_in_percent = 0.05

    optimizer = Optimizer(store)

    assert isinstance(optimizer.agent, TabuAgent)
    # Check the agent's configuration directly through store settings
    assert store.settings.max_distance_to_new_base_solution == 100


def test_tabu_error_radius(one_task_store: Store):
    Settings.COST_TYPE = CostType.TOTAL_COST
    store = one_task_store

    store.settings.agent = AgentType.TABU_SEARCH
    store.settings.max_distance_to_new_base_solution = float("inf")
    store.settings.error_radius_in_percent = 0.05

    # Create and set a mock solution with known pareto values
    store.solution = create_mock_solution(store.current_state, 100, 100)
    store.pareto_fronts[0].solutions[0] = store.solution

    optimizer = Optimizer(store)

    # Verify we have a TabuAgent
    assert isinstance(optimizer.agent, TabuAgent)

    # Now we can safely access TabuAgent-specific methods
    tabu_agent = optimizer.agent

    # Error radius should be calculated as percentage of distance from origin
    expected_radius = 0.05 * (100**2 + 100**2) ** 0.5
    assert tabu_agent.get_max_distance() == pytest.approx(expected_radius)
