from o2.actions.batching_actions.add_date_time_rule_by_enablement_action import (
    AddDateTimeRuleByEnablementAction,
)
from o2.models.days import DAY
from o2.models.self_rating import SelfRatingInput
from o2.models.timetable import TimePeriod
from o2.store import Store
from tests.fixtures.test_helpers import (
    first_valid,
    replace_timetable,
)
from tests.fixtures.timetable_generator import TimetableGenerator


def test_add_date_time_rule_by_enablement_rule_simple(one_task_store: Store):
    # Set Enablement Time
    store = replace_timetable(
        one_task_store,
        # Batch Size of 3
        batch_processing=[TimetableGenerator.batching_size_rule(TimetableGenerator.FIRST_ACTIVITY, 3)],
        # 4 Hour Tasks
        task_resource_distribution=TimetableGenerator.task_resource_distribution_simple(
            [TimetableGenerator.FIRST_ACTIVITY], 4 * 60 * 60
        ),
        # One Task every 24h
        arrival_time_distribution=TimetableGenerator.arrival_time_distribution(24 * 60 * 60, 24 * 60 * 60),
        arrival_time_calendar=TimetableGenerator.arrival_time_calendar(8, 16, days=[DAY.MONDAY]),
        resource_calendars=TimetableGenerator.resource_calendars(8, 16),
    )

    input = SelfRatingInput.from_base_solution(store.solution)

    _, action = first_valid(store, AddDateTimeRuleByEnablementAction.rate_self(store, input))

    assert action is not None
    assert isinstance(action, AddDateTimeRuleByEnablementAction)
    assert action.params["task_id"] == TimetableGenerator.FIRST_ACTIVITY
    assert action.params["time_period"] == TimePeriod.from_start_end(8, 9)


def test_add_date_time_rule_by_enablement_rule_complex(two_tasks_store):
    # We have two tasks, with the second task having a higher waiting time
    # That's because the second task has a high batch count

    store = replace_timetable(
        two_tasks_store,
        # Batch Size of 3
        batch_processing=[
            TimetableGenerator.batching_size_rule(TimetableGenerator.FIRST_ACTIVITY, 1),
            TimetableGenerator.batching_size_rule(TimetableGenerator.SECOND_ACTIVITY, 5),
        ],
        # 2 Hour Tasks
        task_resource_distribution=TimetableGenerator.task_resource_distribution_simple(
            [TimetableGenerator.FIRST_ACTIVITY, TimetableGenerator.SECOND_ACTIVITY],
            2 * 60 * 60,
        ),
        # One Task every 24h
        arrival_time_distribution=TimetableGenerator.arrival_time_distribution(24 * 60 * 60, 24 * 60 * 60),
        arrival_time_calendar=TimetableGenerator.arrival_time_calendar(8, 16, days=[DAY.MONDAY]),
        resource_calendars=TimetableGenerator.resource_calendars(8, 16, False),
    )

    input = SelfRatingInput.from_base_solution(store.solution)

    _, action = first_valid(store, AddDateTimeRuleByEnablementAction.rate_self(store, input))

    assert action is not None
    assert isinstance(action, AddDateTimeRuleByEnablementAction)
    assert action.params["task_id"] == TimetableGenerator.SECOND_ACTIVITY
    # First Task takes 2 hours -> 8:00 -> 10:00, snd task usually gets enabled at 10
    assert action.params["time_period"] == TimePeriod.from_start_end(10, 11)
