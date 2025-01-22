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


def test_remove_date_time_rule_action_additional_rules(store: Store):
    batching_rule = TimetableGenerator.daily_hour_rule_with_day(
        TimetableGenerator.SECOND_ACTIVITY,
        DAY.MONDAY,
        9,
        12,
    )
    batching_rule.firing_rules[0].insert(
        0,
        TimetableGenerator.batching_size_rule(
            TimetableGenerator.SECOND_ACTIVITY, 50
        ).firing_rules[0][0],
    )
    batching_rule.firing_rules[0].append(
        TimetableGenerator.batching_size_rule(
            TimetableGenerator.SECOND_ACTIVITY, 100
        ).firing_rules[0][0]
    )
    batching_rule.firing_rules.append(
        TimetableGenerator.batching_size_rule(
            TimetableGenerator.SECOND_ACTIVITY, 200
        ).firing_rules[0]
    )
    store = replace_timetable(
        store,
        batch_processing=[
            TimetableGenerator.batching_size_rule(TimetableGenerator.FIRST_ACTIVITY, 0),
            batching_rule,
            TimetableGenerator.batching_size_rule(
                TimetableGenerator.THIRD_ACTIVITY, 300
            ),
        ],
    )

    action = RemoveDateTimeRuleAction(
        RemoveDateTimeRuleActionParamsType(
            task_id=TimetableGenerator.SECOND_ACTIVITY,
            day=DAY.MONDAY,
        )
    )

    new_state = action.apply(state=store.base_state)
    assert len(new_state.timetable.batch_processing) == 3
    # We got two sets of or rules, the first includes the size rules, the second only the size rule
    assert len(new_state.timetable.batch_processing[1].firing_rules) == 2
    # We got still two size rules (and part)
    assert len(new_state.timetable.batch_processing[1].firing_rules[0]) == 2
    assert len(new_state.timetable.batch_processing[1].firing_rules[1]) == 1


def test_remove_date_time_rule_action_two_date_time_rules(store: Store):
    # Regression test for the following rule setup:
    # Rule:
    # 	size >= 2
    # OR
    # 	daily_hour >= 12
    # 	AND
    # 	daily_hour < 13
    # 	AND
    # 	week_day = TUESDAY
    # OR
    # 	daily_hour >= 12
    # 	AND
    # 	daily_hour < 13
    # 	AND
    # 	week_day = SUNDAY
    rule = TimetableGenerator.daily_hour_rule_with_day(
        TimetableGenerator.FIRST_ACTIVITY, DAY.THURSDAY, 12, 13
    )
    rule.firing_rules.insert(
        0,
        TimetableGenerator.batching_size_rule(
            TimetableGenerator.FIRST_ACTIVITY, 2
        ).firing_rules[0],
    )
    rule.firing_rules.append(
        TimetableGenerator.daily_hour_rule_with_day(
            TimetableGenerator.FIRST_ACTIVITY, DAY.SUNDAY, 12, 13
        ).firing_rules[0]
    )
    store = replace_timetable(
        store,
        batch_processing=[rule],
    )

    action = RemoveDateTimeRuleAction(
        RemoveDateTimeRuleActionParamsType(
            task_id=TimetableGenerator.FIRST_ACTIVITY,
            day=DAY.SUNDAY,
        )
    )

    new_state = action.apply(state=store.base_state)
    assert len(new_state.timetable.batch_processing) == 1
    assert len(new_state.timetable.batch_processing[0].firing_rules) == 2
    assert len(new_state.timetable.batch_processing[0].firing_rules[0]) == 1
    assert len(new_state.timetable.batch_processing[0].firing_rules[1]) == 3
