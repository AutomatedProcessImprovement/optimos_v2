from dataclasses import replace

from o2.actions.add_resource_action import AddResourceAction
from o2.actions.modify_calendar_by_cost_action import (
    ModifyCalendarByCostAction,
)
from o2.actions.modify_calendar_by_it_action import (
    ModifyCalendarByITAction,
)
from o2.models.days import DAY
from o2.models.self_rating import SelfRatingInput
from o2.models.timetable import Resource, TimePeriod
from o2.store import Store
from tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.timetable_generator import TimetableGenerator


def test_action_creation_one_resource_one_task(one_task_store: Store):
    evaluation, _ = one_task_store.evaluate()
    input = SelfRatingInput.from_base_evaluation(evaluation)

    rating, action = next(AddResourceAction.rate_self(one_task_store, input))

    assert action is not None
    assert "resource_id" in action.params
    assert action.params["resource_id"] == TimetableGenerator.RESOURCE_ID
    assert "task_id" in action.params
    assert action.params["task_id"] == TimetableGenerator.FIRST_ACTIVITY
    assert "clone_resource" in action.params
    assert action.params["clone_resource"]


def test_action_creation_one_resource_two_tasks(two_tasks_store: Store):
    evaluation, _ = two_tasks_store.evaluate()
    input = SelfRatingInput.from_base_evaluation(evaluation)

    rating, action = next(AddResourceAction.rate_self(two_tasks_store, input))

    assert action is not None
    assert "resource_id" in action.params
    assert action.params["resource_id"] == TimetableGenerator.RESOURCE_ID
    assert "task_id" in action.params
    assert action.params["task_id"] == TimetableGenerator.FIRST_ACTIVITY
    assert "remove_task_from_resource" in action.params
    assert action.params["remove_task_from_resource"]


def test_action_creation_two_resources_one_task(one_task_store: Store):
    one_task_store.replaceState(
        # Add a second resource
        timetable=one_task_store.state.timetable.clone_resource(
            TimetableGenerator.RESOURCE_ID,
            [TimetableGenerator.FIRST_ACTIVITY],
        )
    )
    evaluation, _ = one_task_store.evaluate()

    input = SelfRatingInput.from_base_evaluation(evaluation)

    rating, action = next(AddResourceAction.rate_self(one_task_store, input))

    assert action is not None
    assert "resource_id" in action.params
    assert action.params["resource_id"] == TimetableGenerator.RESOURCE_ID
    assert "task_id" in action.params
    assert action.params["task_id"] == TimetableGenerator.FIRST_ACTIVITY
    assert "clone_resource" in action.params
    assert action.params["clone_resource"]


def test_action_creation_two_resources_two_tasks(two_tasks_store: Store):
    two_tasks_store.replaceState(
        # Add a second resource, and limit the first resource to a small time frame
        timetable=two_tasks_store.state.timetable.clone_resource(
            TimetableGenerator.RESOURCE_ID,
            [TimetableGenerator.FIRST_ACTIVITY, TimetableGenerator.SECOND_ACTIVITY],
        ).replace_resource_calendar(TimetableGenerator.resource_calendars(10, 12)[0])
    )

    evaluation, _ = two_tasks_store.evaluate()

    input = SelfRatingInput.from_base_evaluation(evaluation)

    rating, action = next(AddResourceAction.rate_self(two_tasks_store, input))

    assert action is not None
    assert "resource_id" in action.params
    assert Resource.name_is_clone_of(
        action.params["resource_id"], TimetableGenerator.RESOURCE_ID
    )
    assert "task_id" in action.params
    assert action.params["task_id"] == TimetableGenerator.FIRST_ACTIVITY
    assert "remove_task_from_resource" in action.params
    assert action.params["remove_task_from_resource"]