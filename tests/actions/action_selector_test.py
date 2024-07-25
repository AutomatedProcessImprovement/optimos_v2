from dataclasses import replace

import pandas as pd

from o2.actions.action_selector import ActionSelector
from o2.models.self_rating import SelfRatingInput
from o2.store import Store
from tests.fixtures.timetable_generator import TimetableGenerator

pd.options.display.max_columns = None  # type: ignore
pd.options.display.max_rows = None  # type: ignore


def test_no_rules(store: Store):
    store.replaceTimetable(batch_processing=[])
    store.evaluate()

    evaluations = ActionSelector.evaluate_rules(store)
    rating_input = SelfRatingInput.from_rule_evaluations(store, evaluations)
    assert rating_input is None


def test_only_one_rule(store: Store):
    store.replaceTimetable(batch_processing=[store.state.timetable.batch_processing[0]])
    store.evaluate()

    evaluations = ActionSelector.evaluate_rules(store)
    rating_input = SelfRatingInput.from_rule_evaluations(store, evaluations)
    assert rating_input is not None
    best_action = rating_input.most_impactful_rule
    assert best_action.batching_rule_task_id == TimetableGenerator.FIRST_ACTIVITY
    assert best_action.firing_rule_index == (0, 0)


def test_two_rules_one_bigger(two_tasks_store: Store):
    store = two_tasks_store
    small_rule = TimetableGenerator.batching_size_rule(
        TimetableGenerator.SECOND_ACTIVITY, 2, 1
    )
    big_rule = TimetableGenerator.batching_size_rule(
        TimetableGenerator.FIRST_ACTIVITY, 20, 1
    )
    store.replaceTimetable(
        batch_processing=[small_rule, big_rule],
        task_resource_distribution=TimetableGenerator(store.state.bpmn_definition)
        # 1 minute Tasks
        .create_simple_task_resource_distribution(60)
        # TODO: Improve Syntax
        .timetable.task_resource_distribution,
    )
    # Create base evaluation
    store.evaluate()

    evaluations = ActionSelector.evaluate_rules(store)
    rating_input = SelfRatingInput.from_rule_evaluations(store, evaluations)
    assert rating_input is not None
    best_action = rating_input.most_impactful_rule
    assert best_action.batching_rule_task_id == TimetableGenerator.FIRST_ACTIVITY
    assert best_action.firing_rule_index == (0, 0)

    # Check that rule order does not matter
    store.replaceTimetable(batch_processing=[big_rule, small_rule])
    evaluations = ActionSelector.evaluate_rules(store)
    rating_input = SelfRatingInput.from_rule_evaluations(store, evaluations)
    assert rating_input is not None
    best_action_reversed = rating_input.most_impactful_rule

    assert (
        best_action_reversed.batching_rule_task_id == TimetableGenerator.FIRST_ACTIVITY
    )
    assert best_action_reversed.firing_rule_index == (0, 0)
