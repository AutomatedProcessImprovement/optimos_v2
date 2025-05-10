from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from o2.models.evaluation import Evaluation
from o2.models.settings import CostType, Settings
from o2.models.solution import Solution
from o2.models.state import State
from o2.pareto_front import FRONT_STATUS, ParetoFront
from o2.util.helper import random_string
from o2.util.stat_calculation_helper import (
    calculate_averaged_hausdorff_distance,
    calculate_delta_metric,
    calculate_hyperarea,
    calculate_purity,
    distance,
    generational_distance_p2,
)
from tests.fixtures.test_helpers import create_mock_solution


def test_distance():
    # Test basic distance calculation
    assert distance((0, 0), (3, 4)) == 5.0
    assert distance((1, 1), (4, 5)) == 5.0
    assert distance((0, 0), (0, 0)) == 0.0
    assert distance((-1, -1), (1, 1)) == 2.8284271247461903


def test_calculate_hyperarea(simple_state: State):
    # Test empty solutions
    assert calculate_hyperarea([], (10, 10)) == 0.0

    # Create some test solutions
    solution1 = create_mock_solution(simple_state, 2, 8)
    solution2 = create_mock_solution(simple_state, 4, 6)
    solution3 = create_mock_solution(simple_state, 6, 4)
    solution4 = create_mock_solution(simple_state, 8, 2)

    # Test with reference point (10, 10)
    solutions = [solution1, solution2, solution3, solution4]
    area = calculate_hyperarea(solutions, (10, 10))

    # The implementation sorts by descending x and calculates area from right to left:
    # For solution4 (8,2): (10-8)*(10-2) = 2*8 = 16
    # For solution3 (6,4): (8-6)*(10-4) = 2*6 = 12
    # For solution2 (4,6): (6-4)*(10-6) = 2*4 = 8
    # For solution1 (2,8): (4-2)*(10-8) = 2*2 = 4
    expected_area = 16 + 12 + 8 + 4
    assert abs(area - expected_area) < 1e-10


def test_generational_distance_p2(simple_state: State):
    # Test empty sets
    assert generational_distance_p2([], []) == 0.0
    assert generational_distance_p2([], [create_mock_solution(simple_state, 1, 1)]) == 0.0

    # Create test solutions
    set_a = [
        create_mock_solution(simple_state, 1, 1),
        create_mock_solution(simple_state, 2, 2),
    ]
    set_b = [
        create_mock_solution(simple_state, 1, 1),
        create_mock_solution(simple_state, 2, 2),
    ]

    # Calculate GD
    gd = generational_distance_p2(set_a, set_b)

    # Expected GD: sqrt((0^2 + 0^2)/2) = 0
    expected_gd = 0.0
    assert abs(gd - expected_gd) < 1e-10


def test_calculate_averaged_hausdorff_distance(simple_state: State):
    # Test empty sets
    assert calculate_averaged_hausdorff_distance([], []) == 0.0

    # Create test solutions
    front = [
        create_mock_solution(simple_state, 1, 1),
        create_mock_solution(simple_state, 2, 2),
    ]
    reference = [
        create_mock_solution(simple_state, 1, 1),
        create_mock_solution(simple_state, 2, 2),
    ]

    # Calculate averaged Hausdorff distance
    distance = calculate_averaged_hausdorff_distance(front, reference)

    # Expected distance: (0 + 0)/2 = 0
    expected_distance = 0.0
    assert abs(distance - expected_distance) < 1e-10


def test_calculate_delta_metric(simple_state: State):
    # Test empty sets
    assert calculate_delta_metric([], []) == 0.0

    # Create test solutions
    front = [
        create_mock_solution(simple_state, 1, 1),
        create_mock_solution(simple_state, 2, 2),
        create_mock_solution(simple_state, 3, 3),
    ]
    reference = [
        create_mock_solution(simple_state, 0, 0),
        create_mock_solution(simple_state, 4, 4),
    ]

    # Calculate delta metric
    delta = calculate_delta_metric(front, reference)

    # The delta metric should be between 0 and 1
    assert 0 <= delta <= 1


def test_calculate_purity(simple_state: State):
    # Test empty sets
    assert calculate_purity([], []) == 0.0
    assert calculate_purity([], [create_mock_solution(simple_state, 1, 1)]) == 0.0

    # Create test solutions
    front = [
        create_mock_solution(simple_state, 1, 1),
        create_mock_solution(simple_state, 2, 2),
    ]
    reference = [
        create_mock_solution(simple_state, 1, 1),
        create_mock_solution(simple_state, 2, 2),
        create_mock_solution(simple_state, 3, 3),
    ]

    # Calculate purity
    purity = calculate_purity(front, reference)

    # Expected purity: 2/3 = 0.666...
    expected_purity = 2 / 3
    assert abs(purity - expected_purity) < 1e-10
