from dataclasses import replace

import pandas as pd

from o2.pareto_front import FRONT_STATUS, ParetoFront
from o2.types.evaluation import Evaluation
from o2.types.state import State


def test_pareto_front_add(simple_state: State):
    bad_solution = __create_evaluation(10, 10)
    # We set the bpmn_definition to a different value to differentiate the states
    bad_state = replace(simple_state, bpmn_definition="A")
    good_solution = __create_evaluation(5, 5)
    good_state = replace(simple_state, bpmn_definition="B")

    front = ParetoFront()

    # Add the first solution to the front
    front.add(bad_solution, bad_state)

    # Check that the front contains the added solution
    assert bad_solution in front.evaluations
    assert bad_state in front.states

    # Add a second solution that dominates the first solution
    front.add(good_solution, good_state)

    # Check that the first solution is removed from the front
    assert bad_solution not in front.evaluations
    assert bad_state not in front.states
    assert bad_solution in front.removed_solutions
    assert bad_state in front.removed_states

    # Check that the second solution is added to the front
    assert good_solution in front.evaluations
    assert good_state in front.states


def test_is_in_front(simple_state: State):
    front = ParetoFront()

    # Create some evaluations for testing
    base_evaluation = __create_evaluation(5, 5)

    evaluation1 = __create_evaluation(4, 5)
    evaluation2 = __create_evaluation(5, 4)
    evaluation3 = __create_evaluation(10, 10)
    evaluation4 = __create_evaluation(3, 3)

    assert evaluation1.is_dominated_by(base_evaluation) is False
    assert base_evaluation.is_dominated_by(evaluation1) is False
    assert evaluation2.is_dominated_by(base_evaluation) is False
    assert base_evaluation.is_dominated_by(evaluation2) is False
    assert evaluation3.is_dominated_by(base_evaluation) is True
    assert base_evaluation.is_dominated_by(evaluation3) is False
    assert evaluation4.is_dominated_by(base_evaluation) is False
    assert base_evaluation.is_dominated_by(evaluation4) is True

    front.add(base_evaluation, simple_state)

    assert front.is_in_front(evaluation4) == FRONT_STATUS.IS_DOMINATED

    assert front.is_in_front(evaluation1) == FRONT_STATUS.IN_FRONT
    assert front.is_in_front(evaluation2) == FRONT_STATUS.IN_FRONT

    assert front.is_in_front(evaluation3) == FRONT_STATUS.DOMINATES


def __create_evaluation(total_cycle_time, total_cost, total_waiting_time=0):
    return Evaluation(pd.DataFrame(), total_cycle_time, total_cost, total_waiting_time)
