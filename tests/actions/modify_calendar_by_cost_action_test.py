from dataclasses import replace

from o2.actions.modify_calendar_by_cost_action import (
    ModifyCalendarByCostAction,
)
from o2.models.days import DAY
from o2.models.self_rating import SelfRatingInput
from o2.models.timetable import TimePeriod
from o2.store import Store
from tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.test_helpers import (
    first_calendar_first_period_id,
    replace_constraints,
    replace_timetable,
)
from tests.fixtures.timetable_generator import TimetableGenerator


def test_action_creation_simple_shrink(one_task_store: Store):
    input = SelfRatingInput.from_base_solution(one_task_store.solution)

    rating, action = next(ModifyCalendarByCostAction.rate_self(one_task_store, input))

    assert action is not None
    assert "add_hours_before" in action.params
    assert action.params["add_hours_before"] == -1
    assert "add_hours_after" in action.params
    assert action.params["add_hours_after"] == -1
    assert action.params["calendar_id"] == TimetableGenerator.CALENDAR_ID
    assert action.params["period_id"] == first_calendar_first_period_id(one_task_store)


def test_action_creation_simple_removal(one_task_store: Store):
    resource_calendar = replace(
        one_task_store.base_timetable.resource_calendars[0],
        time_periods=[
            TimePeriod.from_start_end(8, 9, DAY.MONDAY),
            TimePeriod.from_start_end(12, 16, DAY.MONDAY),
        ],
    )
    store = replace_timetable(one_task_store, resource_calendars=[resource_calendar])

    input = SelfRatingInput.from_base_solution(store.solution)

    rating, action = next(ModifyCalendarByCostAction.rate_self(store, input))

    assert action is not None
    assert "remove_period" in action.params
    assert action.params["remove_period"] == 1
    assert action.params["calendar_id"] == TimetableGenerator.CALENDAR_ID
    assert action.params["period_id"] == resource_calendar.time_periods[0].id


def test_action_creation_shrink_start(one_task_store: Store):
    store = replace_timetable(
        one_task_store,
        resource_calendars=TimetableGenerator.resource_calendars(8, 16, False),
    )
    store = replace_constraints(
        store,
        resources=ConstraintsGenerator.resource_constraints(
            always_work_masks=ConstraintsGenerator.work_mask(start_time=12, end_time=16)
        ),
    )

    input = SelfRatingInput.from_base_solution(store.solution)

    rating, action = next(ModifyCalendarByCostAction.rate_self(store, input))

    assert action is not None
    assert "add_hours_before" in action.params
    assert action.params["add_hours_before"] == -1
    assert "add_hours_after" not in action.params
    assert action.params["calendar_id"] == TimetableGenerator.CALENDAR_ID
    assert action.params["period_id"] == first_calendar_first_period_id(store)


def test_action_creation_shrink_end(one_task_store: Store):
    store = replace_timetable(
        one_task_store,
        resource_calendars=TimetableGenerator.resource_calendars(8, 16, False),
    )
    store = replace_constraints(
        store,
        resources=ConstraintsGenerator.resource_constraints(
            always_work_masks=ConstraintsGenerator.work_mask(start_time=8, end_time=12)
        ),
    )

    input = SelfRatingInput.from_base_solution(store.solution)

    rating, action = next(ModifyCalendarByCostAction.rate_self(store, input))

    assert action is not None
    assert "add_hours_after" in action.params
    assert action.params["add_hours_after"] == -1
    assert "add_hours_before" not in action.params
    assert action.params["calendar_id"] == TimetableGenerator.CALENDAR_ID
    assert action.params["period_id"] == first_calendar_first_period_id(store)
