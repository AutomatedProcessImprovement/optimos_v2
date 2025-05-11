from o2.actions.batching_actions.modify_size_of_significant_rule_action import (
    ModifySizeOfSignificantRuleAction,
    ModifySizeOfSignificantRuleActionParamsType,
)
from o2.store import Store
from tests.actions.modify_size_rule_base_action_test import helper_rule_matches_size
from tests.fixtures.test_helpers import replace_timetable
from tests.fixtures.timetable_generator import TimetableGenerator


def test_increment_size(store: Store):
    new_size = TimetableGenerator.BATCHING_BASE_SIZE + 1
    first_rule = store.base_timetable.batch_processing[0]

    action = ModifySizeOfSignificantRuleAction(
        ModifySizeOfSignificantRuleActionParamsType(
            task_id=TimetableGenerator.FIRST_ACTIVITY,
            change_size=1,
            duration_fn=store.constraints.get_duration_fn_for_task(TimetableGenerator.FIRST_ACTIVITY),
        )
    )
    new_state = action.apply(state=store.base_state)
    assert first_rule.task_id == new_state.timetable.batch_processing[0].task_id
    assert helper_rule_matches_size(new_state.timetable.batch_processing[0], new_size)


def test_decrement_size(store: Store):
    new_size = TimetableGenerator.BATCHING_BASE_SIZE - 1
    first_rule = store.base_timetable.batch_processing[0]

    action = ModifySizeOfSignificantRuleAction(
        ModifySizeOfSignificantRuleActionParamsType(
            task_id=TimetableGenerator.FIRST_ACTIVITY,
            change_size=-1,
            duration_fn=store.constraints.get_duration_fn_for_task(TimetableGenerator.FIRST_ACTIVITY),
        )
    )
    new_state = action.apply(state=store.base_state)
    assert first_rule.task_id == new_state.timetable.batch_processing[0].task_id
    assert helper_rule_matches_size(new_state.timetable.batch_processing[0], new_size)


def test_decrement_to_one(store: Store):
    store = replace_timetable(
        store,
        batch_processing=[TimetableGenerator.batching_size_rule(TimetableGenerator.FIRST_ACTIVITY, 2)],
    )
    new_size = 1
    first_rule = store.base_timetable.batch_processing[0]
    action = ModifySizeOfSignificantRuleAction(
        ModifySizeOfSignificantRuleActionParamsType(
            task_id=TimetableGenerator.FIRST_ACTIVITY,
            change_size=-1,
            duration_fn=store.constraints.get_duration_fn_for_task(TimetableGenerator.FIRST_ACTIVITY),
        )
    )
    new_state = action.apply(state=store.base_state)
    assert first_rule.task_id == new_state.timetable.batch_processing[0].task_id
    assert helper_rule_matches_size(new_state.timetable.batch_processing[0], new_size)


def test_create_new_rule(store: Store):
    store = replace_timetable(
        store,
        batch_processing=[],
    )
    action = ModifySizeOfSignificantRuleAction(
        ModifySizeOfSignificantRuleActionParamsType(
            task_id=TimetableGenerator.FIRST_ACTIVITY,
            change_size=1,
            duration_fn=store.constraints.get_duration_fn_for_task(TimetableGenerator.FIRST_ACTIVITY),
        )
    )
    new_state = action.apply(state=store.base_state)

    assert len(new_state.timetable.batch_processing) == 1
    assert new_state.timetable.batch_processing[0].task_id == TimetableGenerator.FIRST_ACTIVITY
    assert helper_rule_matches_size(new_state.timetable.batch_processing[0], 2)
