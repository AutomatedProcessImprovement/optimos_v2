import math

import pytest

from o2.agents.agent import NoNewBaseSolutionFoundError
from o2.agents.tabu_agent import TabuAgent
from o2.models.solution import Solution
from o2.pareto_front import FRONT_STATUS

# These fixtures are now available from conftest.py automatically
# No need to explicitly import them


def test_tabu_agent_initialization(mock_store):
    """Test TabuAgent initialization"""
    agent = TabuAgent(mock_store)
    assert agent.store == mock_store
    # Verify it's a subclass of Agent
    assert hasattr(agent, "catalog")
    assert hasattr(agent, "action_generators")


def test_find_new_base_solution_with_proposed_solution(mock_store, better_solution):
    """Test find_new_base_solution with a proposed solution"""
    agent = TabuAgent(mock_store)

    # Create a solution try with a better solution
    solution_try = (FRONT_STATUS.IN_FRONT, better_solution)

    # Mock the solution tree's pop_nearest_solution method to return a proper Solution
    # This is necessary because find_new_base_solution calls _select_new_base_evaluation
    # which calls pop_nearest_solution
    mock_store.solution_tree.pop_nearest_solution.return_value = better_solution

    # Call find_new_base_solution with the proposed solution
    result = agent.find_new_base_solution(solution_try)

    # Verify the result
    assert isinstance(result, Solution)
    assert result == better_solution
    # The function should have called _select_new_base_evaluation with reinsert_current_solution=True
    mock_store.solution_tree.add_solution.assert_called_once_with(mock_store.solution, archive=False)


def test_find_new_base_solution_without_proposed_solution(mock_store, different_solution):
    """Test find_new_base_solution without a proposed solution"""
    agent = TabuAgent(mock_store)

    # Mock the solution tree's pop_nearest_solution method to return a proper Solution
    mock_store.solution_tree.pop_nearest_solution.return_value = different_solution

    # Call find_new_base_solution without a proposed solution
    result = agent.find_new_base_solution(None)

    # Verify the result
    assert result == different_solution
    # Should not have reinserted the current solution
    mock_store.solution_tree.add_solution.assert_not_called()


def test_find_new_base_solution_no_solution_found(mock_store):
    """Test find_new_base_solution when no solution is found"""
    agent = TabuAgent(mock_store)

    # Mock the solution tree's pop_nearest_solution method to return None
    mock_store.solution_tree.pop_nearest_solution.return_value = None

    # Call find_new_base_solution and expect an exception
    with pytest.raises(NoNewBaseSolutionFoundError):
        agent.find_new_base_solution(None)


def test_get_max_distance_with_fixed_value(mock_store):
    """Test get_max_distance with a fixed value in settings"""
    agent = TabuAgent(mock_store)

    # Set a fixed value for max_distance_to_new_base_solution
    mock_store.settings.max_distance_to_new_base_solution = 10.0
    mock_store.settings.error_radius_in_percent = None

    # Call get_max_distance
    result = agent.get_max_distance()

    # Verify the result
    assert result == 10.0


def test_get_max_distance_with_error_radius_percent(mock_store, simple_solution):
    """Test get_max_distance with error_radius_in_percent in settings"""
    agent = TabuAgent(mock_store)

    # Set error_radius_in_percent
    mock_store.settings.max_distance_to_new_base_solution = float("inf")
    mock_store.settings.error_radius_in_percent = 0.1

    # Calculate expected distance
    expected_distance = 0.1 * math.sqrt(simple_solution.pareto_x**2 + simple_solution.pareto_y**2)

    # Call get_max_distance
    result = agent.get_max_distance()

    # Verify the result
    assert result == expected_distance


def test_get_max_distance_with_no_settings(mock_store):
    """Test get_max_distance with no relevant settings"""
    agent = TabuAgent(mock_store)

    # Set both settings to None or inf
    mock_store.settings.max_distance_to_new_base_solution = float("inf")
    mock_store.settings.error_radius_in_percent = None

    # Call get_max_distance
    result = agent.get_max_distance()

    # Verify the result
    assert result == float("inf")


def test_process_many_solutions(mock_store, simple_solution, better_solution, dominated_solution):
    """Test process_many_solutions method"""
    agent = TabuAgent(mock_store)

    # Set error_radius_in_percent for distance calculation
    mock_store.settings.error_radius_in_percent = 0.1

    # Test with a list of solutions
    solutions = [simple_solution, better_solution, dominated_solution]

    # Call process_many_solutions
    chosen, not_chosen = agent.process_many_solutions(solutions)

    # Verify the results
    assert len(chosen) == 1  # Only better_solution should be chosen
    assert len(not_chosen) == 2  # simple_solution and dominated_solution should not be chosen

    # Verify it's the better solution that was chosen
    assert chosen[0][1].evaluation.hourly_rates["_"] == 5


def test_select_new_base_evaluation_with_reinsert(mock_store, different_solution):
    """Test _select_new_base_evaluation with reinsert_current_solution=True"""
    agent = TabuAgent(mock_store)

    # Mock the solution tree's pop_nearest_solution method to return a proper Solution
    mock_store.solution_tree.pop_nearest_solution.return_value = different_solution

    # Call _select_new_base_evaluation with reinsert_current_solution=True
    result = agent._select_new_base_evaluation(reinsert_current_solution=True)

    # Verify the result
    assert result == different_solution
    # Should have reinserted the current solution
    mock_store.solution_tree.add_solution.assert_called_once_with(mock_store.solution, archive=False)


def test_select_new_base_evaluation_without_reinsert(mock_store, different_solution):
    """Test _select_new_base_evaluation with reinsert_current_solution=False"""
    agent = TabuAgent(mock_store)

    # Mock the solution tree's pop_nearest_solution method to return a proper Solution
    mock_store.solution_tree.pop_nearest_solution.return_value = different_solution

    # Call _select_new_base_evaluation with reinsert_current_solution=False
    result = agent._select_new_base_evaluation(reinsert_current_solution=False)

    # Verify the result
    assert result == different_solution
    # Should not have reinserted the current solution
    mock_store.solution_tree.add_solution.assert_not_called()


def test_select_new_base_evaluation_no_solution(mock_store):
    """Test _select_new_base_evaluation when no solution is found"""
    agent = TabuAgent(mock_store)

    # Mock the solution tree's pop_nearest_solution method to return None
    mock_store.solution_tree.pop_nearest_solution.return_value = None

    # Call _select_new_base_evaluation and expect an exception
    with pytest.raises(NoNewBaseSolutionFoundError):
        agent._select_new_base_evaluation()
