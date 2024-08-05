from o2.actions.action_selector import ActionSelector
from o2.actions.modify_calendar_by_wt_action import (
    ModifyCalendarByWTAction,
    ModifyCalendarByWTActionParamsType,
)
from o2.actions.modify_daily_hour_rule_action import (
    ModifyDailyHourRuleAction,
    ModifyDailyHourRuleActionParamsType,
)
from o2.models.days import DAY
from o2.models.rule_selector import RuleSelector
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.state import State
from o2.models.timetable import ResourceCalendar, TimePeriod
from o2.store import Store
from tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.timetable_generator import TimetableGenerator


def test_simple_add_hour(one_task_store: Store):
    one_task_store.replaceTimetable(
        resource_calendars=TimetableGenerator.resource_calendars(8, 16, False)
    )
    action = ModifyCalendarByWTAction(
        ModifyCalendarByWTActionParamsType(
            calendar_id=TimetableGenerator.CALENDAR_ID,
            period_index=0,
            day=DAY.MONDAY,
            shift_hours=0,
            add_hours_before=1,
        )
    )

    one_task_store.apply_action(action)
    calendar = one_task_store.state.timetable.get_calendar(
        TimetableGenerator.CALENDAR_ID
    )
    assert calendar is not None
    assert calendar.get_periods_for_day(DAY.MONDAY) == [
        TimePeriod(
            from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="07:00:00", end_time="16:00:00"
        )
    ]


def test_simple_shift_hour(one_task_store: Store):
    one_task_store.replaceTimetable(
        resource_calendars=TimetableGenerator.resource_calendars(8, 16, False)
    )
    action = ModifyCalendarByWTAction(
        ModifyCalendarByWTActionParamsType(
            calendar_id=TimetableGenerator.CALENDAR_ID,
            period_index=0,
            day=DAY.MONDAY,
            shift_hours=-1,
            add_hours_before=0,
        )
    )

    one_task_store.apply_action(action)
    calendar = one_task_store.state.timetable.get_calendar(
        TimetableGenerator.CALENDAR_ID
    )
    assert calendar is not None
    assert calendar.get_periods_for_day(DAY.MONDAY) == [
        TimePeriod.from_start_end(7, 15)
    ]


def test_action_creation_simple_addition(one_task_store: Store):
    one_task_store.replaceTimetable(
        resource_calendars=TimetableGenerator.resource_calendars(8, 16, False)
    )

    evaluation, _ = one_task_store.evaluate()
    input = SelfRatingInput.from_base_evaluation(evaluation)

    rating, action = ModifyCalendarByWTAction.rate_self(one_task_store, input)

    assert action is not None
    assert action.params["add_hours_before"] == 1
    assert action.params["calendar_id"] == TimetableGenerator.CALENDAR_ID
    assert action.params["period_index"] == 0


def test_action_creation_simple_shift(one_task_store: Store):
    one_task_store.replaceTimetable(
        resource_calendars=TimetableGenerator.resource_calendars(8, 16, False)
    )
    one_task_store.replaceConstraints(
        resources=ConstraintsGenerator.resource_constraints(
            global_constraints=ConstraintsGenerator.global_constraints(
                # Restrict to 8 hours, so we cant just add a new hour
                max_consecutive_cap=8
            )
        )
    )

    evaluation, _ = one_task_store.evaluate()
    input = SelfRatingInput.from_base_evaluation(evaluation)

    rating, action = ModifyCalendarByWTAction.rate_self(one_task_store, input)

    assert action is not None
    assert action.params["shift_hours"] == 1
    assert action.params["calendar_id"] == TimetableGenerator.CALENDAR_ID
    assert action.params["period_index"] == 0


def test_other_days_not_affected(one_task_store: Store):
    one_task_store.replaceTimetable(
        resource_calendars=TimetableGenerator.resource_calendars(8, 16, False)
    )
    evaluation, _ = one_task_store.evaluate()
    input = SelfRatingInput.from_base_evaluation(evaluation)

    rating, action = ModifyCalendarByWTAction.rate_self(one_task_store, input)
    assert action is not None
    one_task_store.apply_action(action)
    new_calendar = one_task_store.state.timetable.get_calendar(
        TimetableGenerator.CALENDAR_ID
    )
    assert new_calendar is not None

    assert new_calendar.time_periods == [
        TimePeriod.from_start_end(7, 16, DAY.MONDAY),
        TimePeriod.from_start_end(8, 16, DAY.TUESDAY),
        TimePeriod.from_start_end(8, 16, DAY.WEDNESDAY),
        TimePeriod.from_start_end(8, 16, DAY.THURSDAY),
        TimePeriod.from_start_end(8, 16, DAY.FRIDAY),
        TimePeriod.from_start_end(8, 16, DAY.SATURDAY),
        TimePeriod.from_start_end(8, 16, DAY.SUNDAY),
    ]
