from dataclasses import replace

import pandas as pd

from o2.models.evaluation import Evaluation
from o2.models.settings import CostType, Settings
from o2.models.solution import Solution
from o2.models.state import State
from o2.pareto_front import FRONT_STATUS, ParetoFront
from o2.util.helper import random_string
from tests.fixtures.test_helpers import create_mock_solution


def test_pareto_front_add(simple_state: State):
    bad_solution = create_mock_solution(simple_state, 10, 10)
    # We set the bpmn_definition to a different value to differentiate the states

    good_solution = create_mock_solution(simple_state, 5, 5)

    front = ParetoFront()

    # Add the first solution to the front
    front.add(bad_solution)

    # Check that the front contains the added solution
    assert bad_solution in front.solutions

    # Add a second solution that dominates the first solution
    front.add(good_solution)

    # Check that the first solution is removed from the front
    assert bad_solution not in front.solutions
    assert bad_solution in front.removed_solutions

    # Check that the second solution is added to the front
    assert good_solution in front.solutions


def test_is_in_front(simple_state: State):
    front = ParetoFront()

    # Create some evaluations for testing
    base_solution = create_mock_solution(simple_state, 5, 5)

    solution1 = create_mock_solution(simple_state, 4, 5)
    solution2 = create_mock_solution(simple_state, 5, 4)
    solution3 = create_mock_solution(simple_state, 10, 10)
    solution4 = create_mock_solution(simple_state, 3, 3)

    assert solution1.is_dominated_by(base_solution) is False
    assert base_solution.is_dominated_by(solution1) is False
    assert solution2.is_dominated_by(base_solution) is False
    assert base_solution.is_dominated_by(solution2) is False
    assert solution3.is_dominated_by(base_solution) is True
    assert base_solution.is_dominated_by(solution3) is False
    assert solution4.is_dominated_by(base_solution) is False
    assert base_solution.is_dominated_by(solution4) is True

    # Test for empty front
    assert front.is_in_front(solution1) == FRONT_STATUS.IN_FRONT

    front.add(base_solution)

    assert front.is_in_front(solution4) == FRONT_STATUS.IS_DOMINATED

    assert front.is_in_front(solution1) == FRONT_STATUS.IN_FRONT
    assert front.is_in_front(solution2) == FRONT_STATUS.IN_FRONT

    assert front.is_in_front(solution3) == FRONT_STATUS.DOMINATES


def test_one_dimension_equal(simple_state: State):
    Settings.EQUAL_DOMINATION_ALLOWED = True

    front = ParetoFront()

    # Create some evaluations for testing
    base_solution = create_mock_solution(simple_state, 5, 5)

    solution1 = create_mock_solution(simple_state, 5, 5)
    solution2 = create_mock_solution(simple_state, 5, 6)
    solution3 = create_mock_solution(simple_state, 6, 5)

    front.add(base_solution)

    assert front.is_in_front(solution1) == FRONT_STATUS.IN_FRONT
    assert front.is_in_front(solution2) == FRONT_STATUS.IN_FRONT
    assert front.is_in_front(solution3) == FRONT_STATUS.IN_FRONT
    Settings.EQUAL_DOMINATION_ALLOWED = False


def test_equal_domination_forbidden(simple_state: State):
    Settings.EQUAL_DOMINATION_ALLOWED = False
    Settings.COST_TYPE = CostType.TOTAL_COST
    front = ParetoFront()

    # Create some evaluations for testing
    base_solution = create_mock_solution(simple_state, 5, 5)

    solution1 = create_mock_solution(simple_state, 5, 5)
    solution2 = create_mock_solution(simple_state, 5, 6)
    solution3 = create_mock_solution(simple_state, 6, 5)

    front.add(base_solution)

    assert front.is_in_front(solution1) == FRONT_STATUS.DOMINATES
    assert front.is_in_front(solution2) == FRONT_STATUS.DOMINATES
    assert front.is_in_front(solution3) == FRONT_STATUS.DOMINATES
