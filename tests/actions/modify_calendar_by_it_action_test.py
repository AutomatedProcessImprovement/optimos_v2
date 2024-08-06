from o2.actions.modify_calendar_by_it_action import (
    ModifyCalendarByITAction,
)
from o2.models.days import DAY
from o2.models.self_rating import SelfRatingInput
from o2.models.timetable import TimePeriod
from o2.store import Store
from tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.timetable_generator import TimetableGenerator


def test_action_creation_simple_addition(one_task_store: Store):
    one_task_store.replaceTimetable(
        resource_calendars=TimetableGenerator.resource_calendars(8, 16, False)
    )

    evaluation, _ = one_task_store.evaluate()
    input = SelfRatingInput.from_base_evaluation(evaluation)

    rating, action = ModifyCalendarByITAction.rate_self(one_task_store, input)

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

    rating, action = ModifyCalendarByITAction.rate_self(one_task_store, input)

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

    rating, action = ModifyCalendarByITAction.rate_self(one_task_store, input)
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
