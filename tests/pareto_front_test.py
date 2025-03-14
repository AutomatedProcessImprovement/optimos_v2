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


def test_pareto_front_real_numbers_regression(simple_state: State):
    Settings.EQUAL_DOMINATION_ALLOWED = False
    Settings.COST_TYPE = CostType.TOTAL_COST

    front = ParetoFront()

    bad_solution = create_mock_solution(simple_state, 37861911, 380455933)
    beating_solution = create_mock_solution(simple_state, 37192569, 328648484)

    assert bad_solution.is_dominated_by(beating_solution) is True
    assert beating_solution.is_dominated_by(bad_solution) is False

    other_solution1 = create_mock_solution(simple_state, 40402802, 282820904)
    other_solution2 = create_mock_solution(simple_state, 40620980, 276613654)
    other_solution3 = create_mock_solution(simple_state, 40647690, 275487327)
    other_solution4 = create_mock_solution(simple_state, 40770083, 275194975)

    front.add(other_solution1)
    front.add(other_solution2)
    front.add(other_solution3)
    front.add(other_solution4)

    front.add(bad_solution)
    front.add(beating_solution)

    assert bad_solution not in front.solutions
    assert beating_solution in front.solutions

    front = ParetoFront()

    front.add(other_solution1)
    front.add(other_solution2)
    front.add(other_solution3)
    front.add(other_solution4)

    front.add(beating_solution)
    assert front.is_in_front(bad_solution) == FRONT_STATUS.DOMINATES


def test_removal_of_multiple_dominated_solutions(simple_state: State):
    front = ParetoFront()

    dominated_solution1 = create_mock_solution(simple_state, 3, 5)
    dominated_solution2 = create_mock_solution(simple_state, 4, 5)
    dominated_solution3 = create_mock_solution(simple_state, 5, 4)
    dominated_solution4 = create_mock_solution(simple_state, 6, 3)

    dominated_solution4 = create_mock_solution(simple_state, 6, 3)

    front.add(dominated_solution1)
    front.add(dominated_solution2)
    front.add(dominated_solution3)
    front.add(dominated_solution4)

    assert dominated_solution1 in front.solutions
    assert dominated_solution2 in front.solutions
    assert dominated_solution3 in front.solutions
    assert dominated_solution4 in front.solutions

    dominating_solution = create_mock_solution(simple_state, 3, 3)

    front.add(dominating_solution)

    assert dominating_solution in front.solutions
    assert dominated_solution1 not in front.solutions
    assert dominated_solution2 not in front.solutions
    assert dominated_solution3 not in front.solutions
    assert dominated_solution4 not in front.solutions
