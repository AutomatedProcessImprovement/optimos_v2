from dataclasses import replace

from o2.actions.modify_calendar_by_cost_action import (
    ModifyCalendarByCostAction,
)
from o2.actions.modify_calendar_by_it_action import (
    ModifyCalendarByITAction,
)
from o2.models.days import DAY
from o2.models.self_rating import SelfRatingInput
from o2.models.timetable import TimePeriod
from o2.store import Store
from tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.timetable_generator import TimetableGenerator


def test_action_creation_simple_shrink(one_task_store: Store):
    evaluation, _ = one_task_store.evaluate()
    input = SelfRatingInput.from_base_solution(evaluation)

    rating, action = next(ModifyCalendarByCostAction.rate_self(one_task_store, input))

    assert action is not None
    assert "add_hours_before" in action.params
    assert action.params["add_hours_before"] == -1
    assert "add_hours_after" in action.params
    assert action.params["add_hours_after"] == -1
    assert action.params["calendar_id"] == TimetableGenerator.CALENDAR_ID
    assert action.params["period_id"] == 0


def test_action_creation_simple_removal(one_task_store: Store):
    resource_calendar = one_task_store.base_solution.timetable.resource_calendars[0]
    resource_calendar = replace(
        resource_calendar,
        time_periods=[
            TimePeriod.from_start_end(8, 9, DAY.MONDAY),
            TimePeriod.from_start_end(12, 16, DAY.MONDAY),
        ],
    )
    one_task_store.replaceTimetable(resource_calendars=[resource_calendar])

    evaluation, _ = one_task_store.evaluate()
    input = SelfRatingInput.from_base_solution(evaluation)

    rating, action = next(ModifyCalendarByCostAction.rate_self(one_task_store, input))

    assert action is not None
    assert "remove_period" in action.params
    assert action.params["remove_period"] == 1
    assert action.params["calendar_id"] == TimetableGenerator.CALENDAR_ID
    assert action.params["period_id"] == 0


def test_action_creation_shrink_start(one_task_store: Store):
    one_task_store.replaceTimetable(
        resource_calendars=TimetableGenerator.resource_calendars(8, 16, False)
    )
    one_task_store.replaceConstraints(
        resources=ConstraintsGenerator.resource_constraints(
            always_work_masks=ConstraintsGenerator.work_mask(start_time=12, end_time=16)
        )
    )

    evaluation, _ = one_task_store.evaluate()
    input = SelfRatingInput.from_base_solution(evaluation)

    rating, action = next(ModifyCalendarByCostAction.rate_self(one_task_store, input))

    assert action is not None
    assert "add_hours_before" in action.params
    assert action.params["add_hours_before"] == -1
    assert "add_hours_after" not in action.params
    assert action.params["calendar_id"] == TimetableGenerator.CALENDAR_ID
    assert action.params["period_id"] == 0


def test_action_creation_shrink_end(one_task_store: Store):
    one_task_store.replaceTimetable(
        resource_calendars=TimetableGenerator.resource_calendars(8, 16, False)
    )
    one_task_store.replaceConstraints(
        resources=ConstraintsGenerator.resource_constraints(
            always_work_masks=ConstraintsGenerator.work_mask(start_time=8, end_time=12)
        )
    )

    evaluation, _ = one_task_store.evaluate()
    input = SelfRatingInput.from_base_solution(evaluation)

    rating, action = next(ModifyCalendarByCostAction.rate_self(one_task_store, input))

    assert action is not None
    assert "add_hours_after" in action.params
    assert action.params["add_hours_after"] == -1
    assert "add_hours_before" not in action.params
    assert action.params["calendar_id"] == TimetableGenerator.CALENDAR_ID
    assert action.params["period_id"] == 0
