from o2.actions.modify_calendar_by_wt_action import (
    ModifyCalendarByWTAction,
    ModifyCalendarByWTActionParamsType,
)
from o2.models.days import DAY
from o2.models.timetable import TimePeriod
from o2.store import Store
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
