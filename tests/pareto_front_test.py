from dataclasses import replace

import pandas as pd
from bpdfr_simulation_engine.simulation_stats_calculator import KPIInfo, KPIMap

from o2.models.evaluation import Evaluation
from o2.models.solution import Solution
from o2.models.state import State
from o2.pareto_front import FRONT_STATUS, ParetoFront
from o2.util.helper import random_string


def test_pareto_front_add(simple_state: State):
    bad_solution = __create_solution(simple_state, 10, 10)
    # We set the bpmn_definition to a different value to differentiate the states

    good_solution = __create_solution(simple_state, 5, 5)

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
    base_solution = __create_solution(simple_state, 5, 5)

    evaluation1 = __create_solution(simple_state, 4, 5)
    evaluation2 = __create_solution(simple_state, 5, 4)
    evaluation3 = __create_solution(simple_state, 10, 10)
    evaluation4 = __create_solution(simple_state, 3, 3)

    assert evaluation1.is_dominated_by(base_solution) is False
    assert base_solution.is_dominated_by(evaluation1) is False
    assert evaluation2.is_dominated_by(base_solution) is False
    assert base_solution.is_dominated_by(evaluation2) is False
    assert evaluation3.is_dominated_by(base_solution) is True
    assert base_solution.is_dominated_by(evaluation3) is False
    assert evaluation4.is_dominated_by(base_solution) is False
    assert base_solution.is_dominated_by(evaluation4) is True

    # Test for empty front
    assert front.is_in_front(evaluation1) == FRONT_STATUS.IN_FRONT

    front.add(base_solution)

    assert front.is_in_front(evaluation4) == FRONT_STATUS.IS_DOMINATED

    assert front.is_in_front(evaluation1) == FRONT_STATUS.IN_FRONT
    assert front.is_in_front(evaluation2) == FRONT_STATUS.IN_FRONT

    assert front.is_in_front(evaluation3) == FRONT_STATUS.DOMINATES


def test_one_dimension_equal(simple_state: State):
    front = ParetoFront()

    # Create some evaluations for testing
    base_solution = __create_solution(simple_state, 5, 5)

    solution1 = __create_solution(simple_state, 5, 5)
    solution2 = __create_solution(simple_state, 5, 6)
    solution3 = __create_solution(simple_state, 6, 5)

    front.add(base_solution)

    assert front.is_in_front(solution1) == FRONT_STATUS.IN_FRONT
    assert front.is_in_front(solution2) == FRONT_STATUS.IN_FRONT
    assert front.is_in_front(solution3) == FRONT_STATUS.IN_FRONT


def __create_solution(state, total_cycle_time, total_cost, total_waiting_time=0):
    kpis = KPIMap()
    kpis.cycle_time = KPIInfo()
    kpis.cycle_time.total = total_cycle_time
    kpis.waiting_time = KPIInfo()
    kpis.waiting_time.total = total_cycle_time
    cost_kpi = KPIMap()
    cost_kpi.cost.total = total_cost

    evaluation = Evaluation(kpis, {"_": cost_kpi}, {}, None)  # type: ignore
    state = replace(state, bpmn_definition=random_string())
    return Solution(evaluation, state, None, [])
