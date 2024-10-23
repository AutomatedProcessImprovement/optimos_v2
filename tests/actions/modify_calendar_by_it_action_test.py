from o2.actions.modify_calendar_by_it_action import (
    ModifyCalendarByITAction,
)
from o2.models.days import DAY
from o2.models.self_rating import SelfRatingInput
from o2.models.timetable import TimePeriod
from o2.store import Store
from tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.test_helpers import (
    first_calendar_first_period_id,
    first_valid,
    replace_constraints,
    replace_timetable,
)
from tests.fixtures.timetable_generator import TimetableGenerator


def test_action_creation_simple_addition(one_task_store: Store):
    store = replace_timetable(
        one_task_store,
        resource_calendars=TimetableGenerator.resource_calendars(8, 16, False),
    )

    input = SelfRatingInput.from_base_solution(store.solution)

    _, action = first_valid(store, ModifyCalendarByITAction.rate_self(store, input))

    assert action is not None
    assert "add_hours_after" in action.params
    assert action.params["add_hours_after"] == 1
    assert action.params["calendar_id"] == TimetableGenerator.CALENDAR_ID
    assert action.params["period_id"] == first_calendar_first_period_id(store)


def test_action_creation_simple_shift(one_task_store: Store):
    store = replace_timetable(
        one_task_store,
        resource_calendars=TimetableGenerator.resource_calendars(8, 16, False),
    )
    store = replace_constraints(
        store,
        resources=ConstraintsGenerator.resource_constraints(
            global_constraints=ConstraintsGenerator.global_constraints(
                # Restrict to 8 hours, so we cant just add a new hour
                max_consecutive_cap=8
            )
        ),
    )

    input = SelfRatingInput.from_base_solution(store.solution)

    _, action = first_valid(store, ModifyCalendarByITAction.rate_self(store, input))

    assert action is not None
    assert "shift_hours" in action.params
    assert action.params["shift_hours"] == 1
    assert action.params["calendar_id"] == TimetableGenerator.CALENDAR_ID
    assert action.params["period_id"] == first_calendar_first_period_id(store)
