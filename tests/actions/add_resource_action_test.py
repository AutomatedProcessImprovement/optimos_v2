from o2.actions.legacy_optimos_actions.add_resource_action import AddResourceAction
from o2.models.self_rating import SelfRatingInput
from o2.store import Store
from o2.util.helper import name_is_clone_of
from tests.fixtures.test_helpers import first_valid, replace_state
from tests.fixtures.timetable_generator import TimetableGenerator


def test_action_creation_one_resource_one_task(one_task_store: Store):
    input = SelfRatingInput.from_base_solution(one_task_store.solution)

    rating, action = first_valid(
        one_task_store, AddResourceAction.rate_self(one_task_store, input)
    )

    assert action is not None
    assert "resource_id" in action.params
    assert action.params["resource_id"] == TimetableGenerator.RESOURCE_ID
    assert "task_id" in action.params
    assert action.params["task_id"] == TimetableGenerator.FIRST_ACTIVITY
    assert "clone_resource" in action.params
    assert action.params["clone_resource"]


def test_action_creation_one_resource_two_tasks(two_tasks_store: Store):
    store = two_tasks_store
    input = SelfRatingInput.from_base_solution(store.solution)

    _, action = first_valid(store, AddResourceAction.rate_self(store, input))

    assert action is not None
    assert "resource_id" in action.params
    assert action.params["resource_id"] == TimetableGenerator.RESOURCE_ID
    assert "task_id" in action.params
    assert action.params["task_id"] == TimetableGenerator.FIRST_ACTIVITY
    assert "remove_task_from_resource" in action.params
    assert action.params["remove_task_from_resource"]


def test_action_creation_two_resources_one_task(one_task_store: Store):
    store = replace_state(
        one_task_store,
        # Add a second resource
        timetable=one_task_store.base_timetable.clone_resource(
            TimetableGenerator.RESOURCE_ID,
            [TimetableGenerator.FIRST_ACTIVITY],
        ),
    )

    input = SelfRatingInput.from_base_solution(store.solution)

    _, action = first_valid(store, AddResourceAction.rate_self(store, input))

    assert action is not None
    assert "resource_id" in action.params
    assert action.params["resource_id"] == TimetableGenerator.RESOURCE_ID
    assert "task_id" in action.params
    assert action.params["task_id"] == TimetableGenerator.FIRST_ACTIVITY
    assert "clone_resource" in action.params
    assert action.params["clone_resource"]


def test_action_creation_two_resources_two_tasks(two_tasks_store: Store):
    store = replace_state(
        two_tasks_store,
        # Add a second resource, and limit the first resource to a small time frame
        timetable=two_tasks_store.base_timetable.clone_resource(
            TimetableGenerator.RESOURCE_ID,
            [TimetableGenerator.FIRST_ACTIVITY, TimetableGenerator.SECOND_ACTIVITY],
        ).replace_resource_calendar(TimetableGenerator.resource_calendars(10, 12)[0]),
    )

    input = SelfRatingInput.from_base_solution(store.solution)

    _, action = first_valid(store, AddResourceAction.rate_self(store, input))

    assert action is not None
    assert "resource_id" in action.params
    assert name_is_clone_of(
        action.params["resource_id"], TimetableGenerator.RESOURCE_ID
    )
    assert "task_id" in action.params
    assert action.params["task_id"] == TimetableGenerator.FIRST_ACTIVITY
    assert "remove_task_from_resource" in action.params
    assert action.params["remove_task_from_resource"]
