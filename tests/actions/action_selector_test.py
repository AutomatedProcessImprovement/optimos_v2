import pandas as pd

from o2.actions.action_selector import ActionSelector
from o2.models.self_rating import SelfRatingInput
from o2.store import Store
from tests.fixtures.test_helpers import replace_timetable
from tests.fixtures.timetable_generator import TimetableGenerator

pd.options.display.max_columns = None  # type: ignore
pd.options.display.max_rows = None  # type: ignore


def test_no_rules(store: Store):
    store = replace_timetable(store, batch_processing=[])

    evaluations = ActionSelector.evaluate_rules(store)
    rating_input = SelfRatingInput.from_rule_solutions(store, evaluations)
    assert rating_input is None


def test_only_one_rule(store: Store):
    store = replace_timetable(
        store, batch_processing=[store.base_state.timetable.batch_processing[0]]
    )

    evaluations = ActionSelector.evaluate_rules(store)
    rating_input = SelfRatingInput.from_rule_solutions(store, evaluations)
    assert rating_input is not None
    best_action = rating_input.most_impactful_rule
    assert best_action is not None
    assert best_action.batching_rule_task_id == TimetableGenerator.FIRST_ACTIVITY
    assert best_action.firing_rule_index == (0, 0)


def test_two_rules_one_bigger(two_tasks_store: Store):
    small_rule = TimetableGenerator.batching_size_rule(
        TimetableGenerator.SECOND_ACTIVITY, 2, 1
    )
    big_rule = TimetableGenerator.batching_size_rule(
        TimetableGenerator.FIRST_ACTIVITY, 20, 1
    )
    store = replace_timetable(
        two_tasks_store,
        batch_processing=[small_rule, big_rule],
    )

    evaluations = ActionSelector.evaluate_rules(store)
    rating_input = SelfRatingInput.from_rule_solutions(store, evaluations)
    assert rating_input is not None
    best_action = rating_input.most_impactful_rule
    assert best_action is not None
    assert best_action.batching_rule_task_id == TimetableGenerator.FIRST_ACTIVITY
    assert best_action.firing_rule_index == (0, 0)

    # Check that rule order does not matter
    store = replace_timetable(store, batch_processing=[big_rule, small_rule])
    evaluations = ActionSelector.evaluate_rules(store)
    rating_input = SelfRatingInput.from_rule_solutions(store, evaluations)
    assert rating_input is not None
    best_action_reversed = rating_input.most_impactful_rule
    assert best_action_reversed is not None
    assert (
        best_action_reversed.batching_rule_task_id == TimetableGenerator.FIRST_ACTIVITY
    )
    assert best_action_reversed.firing_rule_index == (0, 0)
