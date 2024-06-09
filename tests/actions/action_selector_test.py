from dataclasses import replace

import pandas as pd
from o2.store import Store
from o2.actions.action_selector import ActionSelector
from optimos_v2.tests.fixtures.timetable_generator import TimetableGenerator

pd.options.display.max_columns = None  # type: ignore
pd.options.display.max_rows = None  # type: ignore


def test_no_rules(store: Store):
    store.replaceTimetable(batch_processing=[])
    (bestAction, _) = ActionSelector.find_most_impactful_firing_rule(store)
    assert bestAction is None


def test_only_one_rule(store: Store):
    store.replaceTimetable(batch_processing=[store.state.timetable.batch_processing[0]])
    (bestAction, _) = ActionSelector.find_most_impactful_firing_rule(store)
    assert bestAction is not None
    assert bestAction.batching_rule_task_id == TimetableGenerator.FIRST_ACTIVITY
    assert bestAction.firing_rule_index == (0, 0)


def test_two_rules_one_bigger(store: Store):
    small_rule = TimetableGenerator.batching_size_rule(
        TimetableGenerator.SECOND_ACTIVITY, 2
    )
    big_rule = TimetableGenerator.batching_size_rule(
        TimetableGenerator.FIRST_ACTIVITY, 10
    )
    store.replaceTimetable(batch_processing=[small_rule, big_rule])
    bestAction, _ = ActionSelector.find_most_impactful_firing_rule(store)
    assert bestAction is not None
    assert bestAction.batching_rule_task_id == TimetableGenerator.FIRST_ACTIVITY
    assert bestAction.firing_rule_index == (0, 0)

    store.replaceTimetable(batch_processing=[big_rule, small_rule])
    bestActionRev, _ = ActionSelector.find_most_impactful_firing_rule(store)

    assert bestActionRev is not None
    assert bestActionRev.batching_rule_task_id == TimetableGenerator.FIRST_ACTIVITY
    assert bestActionRev.firing_rule_index == (0, 0)
