from dataclasses import replace

import pandas as pd
import pytest

from o2.models.evaluation import Evaluation
from o2.models.settings import CostType, Settings
from o2.models.solution import Solution
from o2.models.state import State
from o2.pareto_front import FRONT_STATUS, ParetoFront
from o2.util.helper import random_string
from tests.fixtures.test_helpers import create_mock_solution


def test_pareto_front_add(simple_state: State):
    Settings.EQUAL_DOMINATION_ALLOWED = False
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
    Settings.EQUAL_DOMINATION_ALLOWED = True
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

    Settings.EQUAL_DOMINATION_ALLOWED = False


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
    Settings.EQUAL_DOMINATION_ALLOWED = True
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


def test_pareto_front_size(simple_state: State):
    """Test the size property of ParetoFront."""
    front = ParetoFront()
    assert front.size == 0

    solution1 = create_mock_solution(simple_state, 10, 10)
    front.add(solution1)
    assert front.size == 1

    solution2 = create_mock_solution(simple_state, 5, 5)
    front.add(solution2)
    # solution1 should be removed as it's dominated
    assert front.size == 1

    solution3 = create_mock_solution(simple_state, 3, 7)
    front.add(solution3)
    # Both solutions are now in the front
    assert front.size == 2


def test_pareto_front_avg_x_avg_y(simple_state: State):
    """Test the avg_x and avg_y properties of ParetoFront."""
    front = ParetoFront()

    solution1 = create_mock_solution(simple_state, 10, 20)
    solution2 = create_mock_solution(simple_state, 20, 10)
    front.add(solution1)
    front.add(solution2)

    assert front.avg_x == 15  # (10 + 20) / 2
    assert front.avg_y == 15  # (20 + 10) / 2


def test_pareto_front_median_x_median_y(simple_state: State):
    """Test the median_x and median_y properties of ParetoFront."""
    front = ParetoFront()

    solution1 = create_mock_solution(simple_state, 10, 30)
    solution2 = create_mock_solution(simple_state, 20, 20)
    solution3 = create_mock_solution(simple_state, 30, 10)
    front.add(solution1)
    front.add(solution2)
    front.add(solution3)

    assert front.median_x == 20  # middle value of [10, 20, 30]
    assert front.median_y == 20  # middle value of [10, 20, 30]


def test_pareto_front_min_max_x_y(simple_state: State):
    """Test the min_x, min_y, max_x, max_y properties of ParetoFront."""
    front = ParetoFront()

    solution1 = create_mock_solution(simple_state, 10, 30)
    solution2 = create_mock_solution(simple_state, 20, 20)
    solution3 = create_mock_solution(simple_state, 30, 10)
    front.add(solution1)
    front.add(solution2)
    front.add(solution3)

    assert front.min_x == 10
    assert front.min_y == 10
    assert front.max_x == 30
    assert front.max_y == 30


def test_pareto_front_avg_cost_metrics(simple_state: State):
    """Test the avg_per_case_cost and avg_total_cost properties of ParetoFront."""
    front = ParetoFront()

    # Create solutions with specific cost values
    solution1 = create_mock_solution(simple_state, 100, 1000)
    solution2 = create_mock_solution(simple_state, 200, 2000)

    front.add(solution1)
    front.add(solution2)

    # Checking the exact values is hard because of how create_mock_solution works
    # Just ensure they're calculated as an average
    assert (
        front.avg_per_case_cost
        == (solution1.evaluation.avg_cost_by_case + solution2.evaluation.avg_cost_by_case) / 2
    )
    assert front.avg_total_cost == (solution1.evaluation.total_cost + solution2.evaluation.total_cost) / 2


def test_pareto_front_cycle_time_metrics(simple_state: State):
    """Test the avg_cycle_time and min_cycle_time properties of ParetoFront."""
    front = ParetoFront()

    # Create solutions with specific cycle time values
    solution1 = create_mock_solution(simple_state, 500, 100)
    solution2 = create_mock_solution(simple_state, 300, 200)

    front.add(solution1)
    front.add(solution2)

    assert front.avg_cycle_time == 400  # (500 + 300) / 2
    assert front.min_cycle_time == 300


def test_pareto_front_avg_point(simple_state: State):
    """Test the avg_point property of ParetoFront."""
    front = ParetoFront()

    solution1 = create_mock_solution(simple_state, 10, 20)
    solution2 = create_mock_solution(simple_state, 20, 10)
    front.add(solution1)
    front.add(solution2)

    assert front.avg_point == (15, 15)  # ((10 + 20) / 2, (20 + 10) / 2)


def test_pareto_front_avg_distance_to(simple_state: State):
    """Test the avg_distance_to method of ParetoFront."""
    front = ParetoFront()

    solution1 = create_mock_solution(simple_state, 10, 20)
    solution2 = create_mock_solution(simple_state, 20, 10)
    target_solution = create_mock_solution(simple_state, 30, 30)

    front.add(solution1)
    front.add(solution2)

    # Calculate expected value manually
    expected_avg_distance = (
        solution1.distance_to(target_solution) + solution2.distance_to(target_solution)
    ) / 2
    assert front.avg_distance_to(target_solution) == expected_avg_distance


def test_pareto_front_is_dominated_by(simple_state: State):
    """Test the is_dominated_by method of ParetoFront."""
    front = ParetoFront()

    solution1 = create_mock_solution(simple_state, 10, 20)
    solution2 = create_mock_solution(simple_state, 20, 10)
    front.add(solution1)
    front.add(solution2)

    # This solution dominates both solutions in the front
    dominating_solution = create_mock_solution(simple_state, 5, 5)
    assert front.is_dominated_by(dominating_solution) == True

    # This solution only dominates one solution in the front
    partial_dominating = create_mock_solution(simple_state, 15, 5)
    assert front.is_dominated_by(partial_dominating) == False


def test_pareto_front_is_dominated_by_evaluation(simple_state: State):
    """Test the is_dominated_by_evaluation method of ParetoFront."""
    front = ParetoFront()

    solution1 = create_mock_solution(simple_state, 10, 20)
    solution2 = create_mock_solution(simple_state, 20, 10)
    front.add(solution1)
    front.add(solution2)

    # Use an evaluation that dominates both solutions in the front
    dominating_solution = create_mock_solution(simple_state, 5, 5)
    dominating_evaluation = dominating_solution.evaluation

    # Use an evaluation that only dominates one solution in the front
    partial_dominating = create_mock_solution(simple_state, 15, 5)
    partial_evaluation = partial_dominating.evaluation

    # Check that the dominating evaluation dominates all solutions in the front
    assert solution1.evaluation.is_dominated_by(dominating_evaluation) == True
    assert solution2.evaluation.is_dominated_by(dominating_evaluation) == True
    assert front.is_dominated_by_evaluation(dominating_evaluation) == True

    # Check that the partial dominating evaluation doesn't dominate all solutions
    assert not (
        solution1.evaluation.is_dominated_by(partial_evaluation)
        and solution2.evaluation.is_dominated_by(partial_evaluation)
    )
    assert front.is_dominated_by_evaluation(partial_evaluation) == False


def test_pareto_front_get_bounding_rect(simple_state: State):
    """Test the get_bounding_rect method of ParetoFront."""
    front = ParetoFront()

    solution1 = create_mock_solution(simple_state, 10, 30)
    solution2 = create_mock_solution(simple_state, 20, 20)
    solution3 = create_mock_solution(simple_state, 30, 10)
    front.add(solution1)
    front.add(solution2)
    front.add(solution3)

    min_x, min_y, max_x, max_y = front.get_bounding_rect()

    assert min_x == 10
    assert min_y == 10
    assert max_x == 30
    assert max_y == 30


def test_pareto_front_empty_front_properties(simple_state: State):
    """Test properties of an empty ParetoFront."""
    front = ParetoFront()

    with pytest.raises(ValueError):  # Min/max/avg of empty sequence raises ValueError
        _ = front.avg_x

    with pytest.raises(ValueError):
        _ = front.avg_y

    with pytest.raises(ValueError):
        _ = front.median_x

    with pytest.raises(ValueError):
        _ = front.median_y

    with pytest.raises(ValueError):
        _ = front.min_x

    with pytest.raises(ValueError):
        _ = front.min_y

    with pytest.raises(ValueError):
        _ = front.max_x

    with pytest.raises(ValueError):
        _ = front.max_y

    with pytest.raises(ValueError):
        _ = front.avg_per_case_cost

    with pytest.raises(ValueError):
        _ = front.avg_total_cost

    with pytest.raises(ValueError):
        _ = front.avg_cycle_time

    with pytest.raises(ValueError):
        _ = front.min_cycle_time

    with pytest.raises(ValueError):
        _ = front.avg_point
