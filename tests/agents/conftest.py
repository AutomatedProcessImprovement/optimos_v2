from unittest import mock

import pytest

from o2.actions.base_actions.base_action import BaseAction
from o2.agents.agent import Agent, NoNewBaseSolutionFoundError
from o2.models.evaluation import Evaluation
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.settings import Settings
from o2.models.solution import Solution
from o2.models.state import State
from o2.pareto_front import FRONT_STATUS, ParetoFront
from o2.store import SolutionTree, SolutionTry, Store
from tests.fixtures.test_helpers import create_mock_solution


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
    return mock.MagicMock(spec=SelfRatingInput)


def mock_action_generator(rating=RATING.HIGH, action=None):
    """Create a mock action generator that yields a single action with the given rating"""
    if action is None:
        action = mock.MagicMock(spec=BaseAction)
        action.id = "mock_action_id"
        action.check_if_valid.return_value = True

    def generator(store, input):
        yield (rating, action)

    return generator
