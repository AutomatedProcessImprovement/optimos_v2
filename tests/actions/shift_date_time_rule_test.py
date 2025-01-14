from o2.actions.base_actions.shift_datetime_rule_base_action import (
    ShiftDateTimeRuleAction,
    ShiftDateTimeRuleBaseActionParamsType,
)
from o2.models.days import DAY
from o2.models.state import State
from tests.fixtures.test_helpers import replace_timetable
from tests.fixtures.timetable_generator import TimetableGenerator


def test_shift_date_time_rule_simple_one_day(one_task_state: State):
    state = one_task_state.replace_timetable(
        batch_processing=[
            TimetableGenerator.daily_hour_rule_with_day(
                TimetableGenerator.FIRST_ACTIVITY,
                DAY.MONDAY,
                9,
                12,
            )
        ],
    )

    action = ShiftDateTimeRuleAction(
        ShiftDateTimeRuleBaseActionParamsType(
            task_id=TimetableGenerator.FIRST_ACTIVITY,
            day=DAY.MONDAY,
            add_to_start=1,
            add_to_end=1,
        )
    )

    new_state = action.apply(state=state)
    assert (
        new_state.timetable.batch_processing[0].firing_rules[0][0].value == DAY.MONDAY
    )
    assert new_state.timetable.batch_processing[0].firing_rules[0][1].value == 8
    assert new_state.timetable.batch_processing[0].firing_rules[0][2].value == 13
    assert len(new_state.timetable.batch_processing[0].firing_rules[0]) == 3
    assert len(new_state.timetable.batch_processing[0].firing_rules) == 1
    assert len(new_state.timetable.batch_processing) == 1


def test_shift_date_time_rule_simple_two_rules_one_day(one_task_state: State):
    batching_rule = TimetableGenerator.batching_size_rule(
        TimetableGenerator.FIRST_ACTIVITY, 1
    )
    batching_rule.firing_rules.append(
        TimetableGenerator.daily_hour_rule_with_day(
            TimetableGenerator.FIRST_ACTIVITY, DAY.MONDAY, 10, 12
        ).firing_rules[0]
    )
    batching_rule.firing_rules.append(
        TimetableGenerator.daily_hour_rule_with_day(
            TimetableGenerator.FIRST_ACTIVITY, DAY.MONDAY, 13, 16
        ).firing_rules[0]
    )
    state = one_task_state.replace_timetable(
        batch_processing=[
            TimetableGenerator.batching_size_rule(
                TimetableGenerator.SECOND_ACTIVITY, 3
            ),
            batching_rule,
            TimetableGenerator.batching_size_rule(TimetableGenerator.THIRD_ACTIVITY, 3),
        ],
    )

    action = ShiftDateTimeRuleAction(
        ShiftDateTimeRuleBaseActionParamsType(
            task_id=TimetableGenerator.FIRST_ACTIVITY,
            day=DAY.MONDAY,
            add_to_start=-1,
            add_to_end=-1,
        )
    )

    new_state = action.apply(state=state)

    # It will select the second rule batching rule and the third rule firing rule,
    # as it is the longest (the first, a size rule, will be ignored)
    assert (
        new_state.timetable.batch_processing[1].firing_rules[2][0].value == DAY.MONDAY
    )
    assert new_state.timetable.batch_processing[1].firing_rules[2][1].value == 14
    assert new_state.timetable.batch_processing[1].firing_rules[2][2].value == 15

    # The other rule should be unchanged
    assert (
        new_state.timetable.batch_processing[1].firing_rules[1][0].value == DAY.MONDAY
    )
    assert new_state.timetable.batch_processing[1].firing_rules[1][1].value == 10
    assert new_state.timetable.batch_processing[1].firing_rules[1][2].value == 12
