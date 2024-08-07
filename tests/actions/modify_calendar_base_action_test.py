from o2.actions.modify_calendar_by_wt_action import (
    ModifyCalendarByWTAction,
    ModifyCalendarByWTActionParamsType,
)
from o2.models.days import DAY
from o2.models.timetable import ResourceCalendar, TimePeriod
from o2.store import Store
from optimos_v2.o2.models.self_rating import SelfRatingInput
from tests.fixtures.timetable_generator import TimetableGenerator

"""
This tests the ModifyCalendarBaseAction abstract class,
by example of the ModifyCalendarByWTAction class.
"""


def test_simple_add_hour(one_task_store: Store):
    one_task_store.replaceTimetable(
        resource_calendars=TimetableGenerator.resource_calendars(8, 16, False)
    )
    action = ModifyCalendarByWTAction(
        ModifyCalendarByWTActionParamsType(
            calendar_id=TimetableGenerator.CALENDAR_ID,
            period_index=0,
            day=DAY.MONDAY,
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
    assert _ensure_other_days_not_affected(calendar)


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
    assert _ensure_other_days_not_affected(calendar)


def test_add_hour_before_and_after(one_task_store: Store):
    one_task_store.replaceTimetable(
        resource_calendars=TimetableGenerator.resource_calendars(8, 16, False)
    )
    action = ModifyCalendarByWTAction(
        ModifyCalendarByWTActionParamsType(
            calendar_id=TimetableGenerator.CALENDAR_ID,
            period_index=0,
            day=DAY.MONDAY,
            add_hours_before=1,
            add_hours_after=1,
        )
    )

    one_task_store.apply_action(action)
    calendar = one_task_store.state.timetable.get_calendar(
        TimetableGenerator.CALENDAR_ID
    )
    assert calendar is not None
    assert calendar.get_periods_for_day(DAY.MONDAY) == [
        TimePeriod(
            from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="07:00:00", end_time="17:00:00"
        )
    ]
    assert _ensure_other_days_not_affected(calendar)


def test_remove_period(one_task_store: Store):
    one_task_store.replaceTimetable(
        resource_calendars=TimetableGenerator.resource_calendars(8, 16, False)
    )
    action = ModifyCalendarByWTAction(
        ModifyCalendarByWTActionParamsType(
            calendar_id=TimetableGenerator.CALENDAR_ID,
            period_index=0,
            day=DAY.MONDAY,
            remove_period=True,
        )
    )

    one_task_store.apply_action(action)
    calendar = one_task_store.state.timetable.get_calendar(
        TimetableGenerator.CALENDAR_ID
    )
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
