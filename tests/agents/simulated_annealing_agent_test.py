import math
from unittest import mock

import pytest

from o2.agents.agent import NoNewBaseSolutionFoundError
from o2.agents.simulated_annealing_agent import DISTANCE_MULTIPLIER, SimulatedAnnealingAgent
from o2.pareto_front import FRONT_STATUS

# These fixtures are now available from conftest.py automatically
# No need to explicitly import them


def test_simulated_annealing_initialization_with_numeric_temperature(mock_store):
    """Test initialization with numeric temperature"""
    # Set a specific temperature
    mock_store.settings.sa_initial_temperature = 50.0
    mock_store.settings.sa_cooling_factor = 0.95

    agent = SimulatedAnnealingAgent(mock_store)

    # Check that the temperature was set correctly
    assert agent.temperature == 50.0
    assert mock_store.settings.sa_cooling_factor == 0.95


def test_simulated_annealing_initialization_with_auto_temperature(mock_store, simple_solution):
    """Test initialization with 'auto' temperature"""
    # Set auto temperature and cooling factor
    mock_store.settings.sa_initial_temperature = "auto"
    mock_store.settings.sa_cooling_factor = 0.95

    agent = SimulatedAnnealingAgent(mock_store)

    # Check that the temperature was calculated correctly
    expected_temp = math.sqrt(simple_solution.pareto_x**2 + simple_solution.pareto_y**2) * DISTANCE_MULTIPLIER
    assert agent.temperature == expected_temp


def test_simulated_annealing_initialization_with_auto_cooling_factor(mock_store, simple_solution):
    """Test initialization with 'auto' cooling factor"""
    # Set up settings for auto cooling factor
    mock_store.settings.sa_initial_temperature = 100.0
    mock_store.settings.sa_cooling_factor = "auto"
    mock_store.settings.error_radius_in_percent = 0.1
    mock_store.settings.sa_cooling_iteration_percent = 0.8
    mock_store.settings.max_iterations = 100
    mock_store.settings.max_number_of_actions_per_iteration = 5
    mock_store.settings.max_solutions = None

    agent = SimulatedAnnealingAgent(mock_store)

    # Check that a cooling factor was calculated
    assert 0 < float(mock_store.settings.sa_cooling_factor) < 1


@pytest.mark.parametrize("has_error_radius", [True, False])
def test_find_new_base_solution_temperature_cooling(mock_store, has_error_radius, simple_solution):
    """Test that temperature cools down in find_new_base_solution"""
    # Configure settings
    mock_store.settings.sa_initial_temperature = 100.0
    mock_store.settings.sa_cooling_factor = 0.95
    mock_store.settings.error_radius_in_percent = 0.1 if has_error_radius else None

    # Set up the agent
    agent = SimulatedAnnealingAgent(mock_store)
    # Get the initial temperature and ensure it's a float
    initial_temp = float(agent.temperature)

    # Store the expected temperature for later comparison
    # We'll manually calculate it to avoid type issues
    cooling_factor = 0.95
    expected_temp = initial_temp * cooling_factor

    # If we have error radius, we need to calculate min temperature
    if has_error_radius:
        min_radius = 0.1 * math.sqrt(mock_store.solution.pareto_x**2 + mock_store.solution.pareto_y**2)
        expected_temp = max(min_radius, expected_temp)

    # Create a properly mocked solution to be returned
    # Instead of using a MagicMock directly, use a real Solution from the fixture
    if mock_store.settings.sa_strict_ordered:
        # This will be returned by get_nearest_solution
        mock_store.solution_tree.get_nearest_solution.return_value = simple_solution
    else:
        # This will be returned by get_random_solution_near_to_pareto_front
        mock_store.solution_tree.get_random_solution_near_to_pareto_front.return_value = simple_solution

    # Call find_new_base_solution
    agent.find_new_base_solution(None)

    # Check that temperature was cooled down - with a delta for floating point
    # Convert agent.temperature to float to avoid type issues
    actual_temp = float(agent.temperature)
    assert abs(actual_temp - expected_temp) < 0.001


def test_find_new_base_solution_with_dominated_solution(mock_store, dominated_solution):
    """Test find_new_base_solution with a dominated solution"""
    # Configure settings
    mock_store.settings.sa_initial_temperature = 100.0
    mock_store.settings.sa_cooling_factor = 0.95
    mock_store.settings.sa_strict_ordered = False

    # Set up the agent
    agent = SimulatedAnnealingAgent(mock_store)

    # Create a solution try with dominated solution
    solution_try = (FRONT_STATUS.DOMINATES, dominated_solution)

    # Mock _accept_worse_solution to accept the dominated solution
    with mock.patch.object(agent, "_accept_worse_solution", return_value=True):
        result = agent.find_new_base_solution(solution_try)

        # Should return the dominated solution
        assert result == dominated_solution


def test_find_new_base_solution_with_strict_ordered(mock_store, different_solution):
    """Test find_new_base_solution with strict_ordered=True"""
    # Configure settings
    mock_store.settings.sa_initial_temperature = 100.0
    mock_store.settings.sa_cooling_factor = 0.95
    mock_store.settings.sa_strict_ordered = True

    # Set up the agent
    agent = SimulatedAnnealingAgent(mock_store)

    # Mock get_nearest_solution to return a proper Solution object
    mock_store.solution_tree.get_nearest_solution.return_value = different_solution

    # Call find_new_base_solution
    result = agent.find_new_base_solution(None)

    # Check that the nearest solution was returned
    assert result == different_solution
    # Verify get_nearest_solution was called, not get_random_solution
    mock_store.solution_tree.get_nearest_solution.assert_called_once()
    mock_store.solution_tree.get_random_solution_near_to_pareto_front.assert_not_called()


def test_find_new_base_solution_with_random_selection(mock_store, different_solution):
    """Test find_new_base_solution with strict_ordered=False"""
    # Configure settings
    mock_store.settings.sa_initial_temperature = 100.0
    mock_store.settings.sa_cooling_factor = 0.95
    mock_store.settings.sa_strict_ordered = False

    # Set up the agent
    agent = SimulatedAnnealingAgent(mock_store)

    # Mock get_random_solution_near_to_pareto_front to return a proper Solution object
    mock_store.solution_tree.get_random_solution_near_to_pareto_front.return_value = different_solution

    # Call find_new_base_solution
    result = agent.find_new_base_solution(None)

    # Check that a random solution was returned
    assert result == different_solution
    # Verify get_random_solution_near_to_pareto_front was called, not get_nearest_solution
    mock_store.solution_tree.get_nearest_solution.assert_not_called()
    mock_store.solution_tree.get_random_solution_near_to_pareto_front.assert_called_once()


def test_find_new_base_solution_no_solution_found(mock_store):
    """Test find_new_base_solution when no solution is found"""
    # Configure settings
    mock_store.settings.sa_initial_temperature = 100.0
    mock_store.settings.sa_cooling_factor = 0.95
    mock_store.settings.sa_strict_ordered = True

    # Set up the agent
    agent = SimulatedAnnealingAgent(mock_store)

    # Mock get_nearest_solution to return None
    mock_store.solution_tree.get_nearest_solution.return_value = None

    # Call find_new_base_solution and expect an exception
    with pytest.raises(NoNewBaseSolutionFoundError):
        agent.find_new_base_solution(None)


def test_accept_worse_solution_probability(mock_store):
    """Test _accept_worse_solution probability calculation"""
    # Configure settings
    mock_store.settings.sa_initial_temperature = 100.0
    mock_store.settings.sa_cooling_factor = 0.95

    # Set up the agent
    agent = SimulatedAnnealingAgent(mock_store)

    # Test with different distances and temperatures
    # High temperature should have higher acceptance probability than low temperature
    distance = 10.0
    high_temp = 100.0
    low_temp = 10.0

    # Mock random.random to return a value that will make high temp accept but low temp reject
    with mock.patch("random.random", return_value=0.5):
        # With high temperature, probability is higher, so should accept
        assert agent._accept_worse_solution(distance, high_temp) is True

        # With low temperature, probability is lower, so should reject
        assert agent._accept_worse_solution(distance, low_temp) is False


def test_select_new_base_evaluation_with_reinsert(mock_store, different_solution):
    """Test _select_new_base_evaluation with reinsert_current_solution=True"""
    # Configure settings
    mock_store.settings.sa_initial_temperature = 100.0
    mock_store.settings.sa_cooling_factor = 0.95
    mock_store.settings.sa_strict_ordered = True

    # Set up the agent
    agent = SimulatedAnnealingAgent(mock_store)

    # Mock get_nearest_solution to return a proper Solution object
    mock_store.solution_tree.get_nearest_solution.return_value = different_solution

    # Call _select_new_base_evaluation with reinsert_current_solution=True
    result = agent._select_new_base_evaluation(reinsert_current_solution=True)

    # Verify the result
    assert result == different_solution
    # Should have reinserted the current solution
    mock_store.solution_tree.add_solution.assert_called_once_with(mock_store.solution, archive=True)
    # Should have removed the selected solution from the tree
    mock_store.solution_tree.remove_solution.assert_called_once_with(different_solution)
