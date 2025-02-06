from o2.actions.legacy_optimos_actions.modify_calendar_by_wt_action import (
    ModifyCalendarByWTAction,
    ModifyCalendarByWTActionParamsType,
)
from o2.models.days import DAY
from o2.models.solution import Solution
from o2.models.timetable import ResourceCalendar, TimePeriod
from o2.store import Store
from tests.fixtures.test_helpers import replace_timetable
from tests.fixtures.timetable_generator import TimetableGenerator

"""
This tests the ModifyCalendarBaseAction abstract class,
by example of the ModifyCalendarByWTAction class.
"""


def test_simple_add_hour(one_task_store: Store):
    resource_calendars = TimetableGenerator.resource_calendars(8, 16, False)
    store = replace_timetable(
        one_task_store,
        resource_calendars=resource_calendars,
    )
    period_id = resource_calendars[0].time_periods[0].id
    action = ModifyCalendarByWTAction(
        ModifyCalendarByWTActionParamsType(
            calendar_id=TimetableGenerator.CALENDAR_ID,
            period_id=period_id,
            day=DAY.MONDAY,
            add_hours_before=1,
        )
    )

    store.run_action(action)

    calendar = store.current_timetable.get_calendar(TimetableGenerator.CALENDAR_ID)
    assert calendar is not None
    assert calendar.get_periods_for_day(DAY.MONDAY) == [
        TimePeriod(
            from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="07:00:00", end_time="16:00:00"
        )
    ]
    assert _ensure_other_days_not_affected(calendar)


def test_simple_shift_hour(one_task_store: Store):
    resource_calendars = TimetableGenerator.resource_calendars(8, 16, False)
    store = replace_timetable(one_task_store, resource_calendars=resource_calendars)
    period_id = resource_calendars[0].time_periods[0].id
    action = ModifyCalendarByWTAction(
        ModifyCalendarByWTActionParamsType(
            calendar_id=TimetableGenerator.CALENDAR_ID,
            period_id=period_id,
            day=DAY.MONDAY,
            shift_hours=-1,
        )
    )

    store.run_action(action)
    calendar = store.current_timetable.get_calendar(TimetableGenerator.CALENDAR_ID)
    assert calendar is not None
    assert calendar.get_periods_for_day(DAY.MONDAY) == [
        TimePeriod.from_start_end(7, 15)
    ]
    assert _ensure_other_days_not_affected(calendar)


def test_add_hour_before_and_after(one_task_store: Store):
    resource_calendars = TimetableGenerator.resource_calendars(8, 16, False)
    store = replace_timetable(one_task_store, resource_calendars=resource_calendars)
    period_id = resource_calendars[0].time_periods[0].id
    action = ModifyCalendarByWTAction(
        ModifyCalendarByWTActionParamsType(
            calendar_id=TimetableGenerator.CALENDAR_ID,
            period_id=period_id,
            day=DAY.MONDAY,
            add_hours_before=1,
            add_hours_after=1,
        )
    )

    store.run_action(action)
    calendar = store.current_timetable.get_calendar(TimetableGenerator.CALENDAR_ID)
    assert calendar is not None
    assert calendar.get_periods_for_day(DAY.MONDAY) == [
        TimePeriod(
            from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="07:00:00", end_time="17:00:00"
        )
    ]
    assert _ensure_other_days_not_affected(calendar)


def test_remove_period(one_task_store: Store):
    resource_calendars = TimetableGenerator.resource_calendars(8, 16, False)
    store = replace_timetable(one_task_store, resource_calendars=resource_calendars)
    period_id = resource_calendars[0].time_periods[0].id

    action = ModifyCalendarByWTAction(
        ModifyCalendarByWTActionParamsType(
            calendar_id=TimetableGenerator.CALENDAR_ID,
            period_id=period_id,
            day=DAY.MONDAY,
            remove_period=True,
        )
    )

    store.run_action(action)
    calendar = store.current_timetable.get_calendar(TimetableGenerator.CALENDAR_ID)
    assert calendar is not None
    assert calendar.get_periods_for_day(DAY.MONDAY) == []
    assert _ensure_other_days_not_affected(calendar)


def _ensure_other_days_not_affected(new_calendar: ResourceCalendar) -> bool:
    time_periods_for_monday = new_calendar.get_periods_for_day(DAY.MONDAY)
    return new_calendar.time_periods == time_periods_for_monday + [
        TimePeriod.from_start_end(8, 16, DAY.TUESDAY),
        TimePeriod.from_start_end(8, 16, DAY.WEDNESDAY),
        TimePeriod.from_start_end(8, 16, DAY.THURSDAY),
        TimePeriod.from_start_end(8, 16, DAY.FRIDAY),
        TimePeriod.from_start_end(8, 16, DAY.SATURDAY),
        TimePeriod.from_start_end(8, 16, DAY.SUNDAY),
    ]
