from typing import Any, List, cast
from unittest import mock

import pytest

from o2.actions.base_actions.base_action import BaseAction
from o2.agents.agent import Agent, NoNewBaseSolutionFoundError
from o2.models.self_rating import RATING
from o2.models.settings import Settings
from o2.models.solution import Solution
from o2.models.state import State
from o2.pareto_front import FRONT_STATUS, ParetoFront
from o2.store import SolutionTree, SolutionTry, Store
from tests.fixtures.test_helpers import create_mock_solution


# Create a concrete Agent subclass for testing
class TestAgent(Agent):
    """Test implementation of Agent for testing purposes."""

    def find_new_base_solution(self, solution_try):
        """Implement the abstract method required by the Agent class."""
        if solution_try:
            return solution_try[1]  # Return the solution part of the solution_try
        return self.store.solution


# Create a mock action class with rate_self method that inherits from BaseAction
class MockActionClass(BaseAction):
    """Mock action class that can be used in the Agent's catalog."""

    def __init__(self, *args, **kwargs):
        """Initialize the MockActionClass."""
        super().__init__(*args, **kwargs)
        # Note: We can't set id directly due to dataclass frozen constraints

    def apply(self, state, **kwargs):
        """Mock implementation of apply that returns the state unchanged."""
        return state

    def check_if_valid(self, store, **kwargs):
        """Mock implementation of check_if_valid that always returns True."""
        return True

    @classmethod
    def rate_self(cls, store, input):
        """Mock implementation of rate_self that returns a fixed action."""
        action = mock.MagicMock(spec=BaseAction)
        action.id = "mock_action_id"
        action.check_if_valid.return_value = True

        def mock_apply(state):
            return state

        action.apply.side_effect = mock_apply

        yield (RATING.HIGH, action)


@pytest.fixture
def simple_solution(simple_state: State):
    """Create a simple solution"""
    return create_mock_solution(simple_state, 10, 10)


@pytest.fixture
def better_solution(simple_state: State):
    """Create a solution that dominates the simple_solution"""
    return create_mock_solution(simple_state, 5, 5)


@pytest.fixture
def different_solution(simple_state: State):
    """Create a solution on the pareto front with the simple_solution"""
    return create_mock_solution(simple_state, 8, 5)


@pytest.fixture
def dominated_solution(simple_state: State):
    """Create a solution dominated by the simple_solution"""
    return create_mock_solution(simple_state, 15, 15)


@pytest.fixture
def mock_store(simple_state: State, simple_solution: Solution):
    """Create a mocked store with a pareto front and solution tree"""
    # Create a store with a simple base solution
    store = mock.MagicMock(spec=Store)
    store.solution = simple_solution
    store.base_evaluation = simple_solution.evaluation

    # Set up the pareto front
    store.current_pareto_front = ParetoFront()
    store.current_pareto_front.add(simple_solution)

    # Set up the solution tree
    store.solution_tree = mock.MagicMock(spec=SolutionTree)

    # Set up default settings
    store.settings = Settings()
    store.settings.max_number_of_actions_per_iteration = 1

    # Mock the try_solution method
    def mock_try_solution(solution):
        status = store.current_pareto_front.is_in_front(solution)
        return (status, solution)

    store.try_solution.side_effect = mock_try_solution

    # Mock the process_many_solutions method
    def mock_process_many(solutions, callback=None):
        chosen = []
        not_chosen = []
        for sol in solutions:
            status = store.current_pareto_front.is_in_front(sol)
            solution_try = (status, sol)
            if status == FRONT_STATUS.IN_FRONT or status == FRONT_STATUS.IS_DOMINATED:
                chosen.append(solution_try)
                if status == FRONT_STATUS.IN_FRONT:
                    store.current_pareto_front.add(sol)
            else:
                not_chosen.append(solution_try)
        return chosen, not_chosen

    store.process_many_solutions.side_effect = mock_process_many

    # Mock is_tabu method
    store.is_tabu.return_value = False

    return store


@pytest.fixture
def mock_action():
    """Create a mock action"""
    action = mock.MagicMock(spec=BaseAction)
    action.id = "mock_action_id"
    action.check_if_valid.return_value = True

    # Mock the apply method
    def mock_apply(state):
        return state

    action.apply.side_effect = mock_apply

    return action


@pytest.fixture
def mock_self_rating_input():
    """Create a mock self rating input"""
    return mock.MagicMock(spec=Solution)


def create_random_mock_agent(agent_class, store):
    """Create a mock agent with a random catalog"""
    agent = agent_class(store)
    # Use MockActionClass with type casting to satisfy type checking
    agent.catalog = cast(List[type[BaseAction]], [MockActionClass])
    return agent


def test_agent_initialization(mock_store):
    """Test that the base Agent class initializes correctly"""
    agent = TestAgent(mock_store)
    assert agent.store == mock_store
    assert isinstance(agent.catalog, list)
    assert hasattr(agent, "action_generators")
    assert hasattr(agent, "action_generator_tabu_ids")
    assert hasattr(agent, "action_generator_counter")


def test_agent_set_action_generators(mock_store, simple_solution, mock_self_rating_input):
    """Test that the set_action_generators method works correctly"""
    with mock.patch("o2.models.self_rating.SelfRatingInput.from_base_solution") as mock_from_base:
        mock_from_base.return_value = mock_self_rating_input

        agent = TestAgent(mock_store)
        # Use MockActionClass with type casting
        agent.catalog = cast(List[type[BaseAction]], [MockActionClass])

        agent.set_action_generators(simple_solution)

        assert len(agent.action_generators) == 1
        assert agent.action_generator_tabu_ids == set()
        assert agent.action_generator_counter == {}


def test_agent_get_valid_actions(mock_store, mock_action):
    """Test that the get_valid_actions method returns valid actions"""
    agent = TestAgent(mock_store)

    # Set up a mock action generator
    mock_generator = mock.MagicMock()
    mock_generator.__iter__.return_value = [(RATING.HIGH, mock_action)]

    agent.action_generators = [mock_generator]
    agent.action_generator_tabu_ids = set()

    # Call get_valid_actions
    actions = agent.get_valid_actions()

    # Check the results
    assert len(actions) == 1
    assert actions[0] == (RATING.HIGH, mock_action)


def test_agent_select_actions(mock_store, mock_action):
    """Test that the select_actions method returns the correct actions"""
    agent = TestAgent(mock_store)

    # Directly mock the get_valid_actions method to avoid infinite loop
    with mock.patch.object(agent, "get_valid_actions") as mock_get_valid_actions:
        # Set up mock return value
        mock_get_valid_actions.return_value = [(RATING.HIGH, mock_action)]

        # Set iterations to a positive number to prevent loop
        agent.iterations_per_solution = 1

        # Call select_actions
        actions = agent.select_actions()

        # Verify mock was called
        mock_get_valid_actions.assert_called_once()

        # Check results
        assert actions is not None
        assert len(actions) == 1
        assert actions[0] == mock_action
