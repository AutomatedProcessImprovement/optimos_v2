from dataclasses import replace

import pandas as pd
from o2.store import Store
from o2.actions.action_selector import ActionSelector
from o2.types.self_rating import SelfRatingInput
from optimos_v2.tests.fixtures.timetable_generator import TimetableGenerator

pd.options.display.max_columns = None  # type: ignore
pd.options.display.max_rows = None  # type: ignore


def test_no_rules(store: Store):
    store.replaceTimetable(batch_processing=[])
    evaluations = ActionSelector.evaluate_rules(store)
    rating_input = SelfRatingInput.from_rule_evaluations(evaluations)
    assert rating_input is None


def test_only_one_rule(store: Store):
    store.replaceTimetable(batch_processing=[store.state.timetable.batch_processing[0]])
    evaluations = ActionSelector.evaluate_rules(store)
    rating_input = SelfRatingInput.from_rule_evaluations(evaluations)
    assert rating_input is not None
    bestAction = rating_input.most_impactful_rule
    assert bestAction.batching_rule_task_id == TimetableGenerator.FIRST_ACTIVITY
    assert bestAction.firing_rule_index == (0, 0)


def test_two_rules_one_bigger(store: Store):
    small_rule = TimetableGenerator.batching_size_rule(
        TimetableGenerator.SECOND_ACTIVITY, 2, 1
    )
    big_rule = TimetableGenerator.batching_size_rule(
        TimetableGenerator.FIRST_ACTIVITY, 20, 1
    )
    store.replaceTimetable(batch_processing=[small_rule, big_rule])
    evaluations = ActionSelector.evaluate_rules(store)
    rating_input = SelfRatingInput.from_rule_evaluations(evaluations)
    assert rating_input is not None
    bestAction = rating_input.most_impactful_rule
    assert bestAction.batching_rule_task_id == TimetableGenerator.FIRST_ACTIVITY
    assert bestAction.firing_rule_index == (0, 0)

    store.replaceTimetable(batch_processing=[big_rule, small_rule])
    evaluations = ActionSelector.evaluate_rules(store)
    rating_input = SelfRatingInput.from_rule_evaluations(evaluations)
    assert rating_input is not None
    bestActionRev = rating_input.most_impactful_rule

    assert bestActionRev.batching_rule_task_id == TimetableGenerator.FIRST_ACTIVITY
    assert bestActionRev.firing_rule_index == (0, 0)
