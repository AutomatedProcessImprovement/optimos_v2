from o2.actions.new_actions.remove_date_time_rule_action import (
    RemoveDateTimeRuleAction,
    RemoveDateTimeRuleActionParamsType,
)
from o2.models.days import DAY
from o2.store import Store
from tests.fixtures.test_helpers import replace_timetable
from tests.fixtures.timetable_generator import TimetableGenerator


def test_remove_date_time_rule_action_simple(store: Store):
    store = replace_timetable(
        store,
        batch_processing=[
            TimetableGenerator.daily_hour_rule_with_day(
                TimetableGenerator.FIRST_ACTIVITY,
                DAY.MONDAY,
                9,
                12,
            )
        ],
    )

    action = RemoveDateTimeRuleAction(
        RemoveDateTimeRuleActionParamsType(
            task_id=TimetableGenerator.FIRST_ACTIVITY,
            day=DAY.MONDAY,
        )
    )

    new_state = action.apply(state=store.base_state)
    assert len(new_state.timetable.batch_processing) == 0

