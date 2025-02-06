from o2.actions.batching_actions.add_date_time_rule_by_availability import (
    AddDateTimeRuleByAvailabilityAction,
)
from o2.models.days import DAY
from o2.models.self_rating import SelfRatingInput
from o2.models.timetable import ResourceCalendar, TimePeriod
from o2.store import Store
from tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.test_helpers import (
    first_valid,
    replace_constraints,
    replace_timetable,
)
from tests.fixtures.timetable_generator import TimetableGenerator


def test_add_date_time_rule_by_availability_simple(one_task_store: Store):
    # Set Enablement Time
    store = replace_timetable(
        one_task_store,
        # Batch Size of 3
        batch_processing=[
            TimetableGenerator.batching_size_rule(TimetableGenerator.FIRST_ACTIVITY, 3)
        ],
        # 1 Hour Tasks
        task_resource_distribution=TimetableGenerator.task_resource_distribution_simple(
            [TimetableGenerator.FIRST_ACTIVITY], 1 * 60 * 60
        ),
        # One Task every 24h
        arrival_time_distribution=TimetableGenerator.arrival_time_distribution(
            24 * 60 * 60, 24 * 60 * 60
        ),
        arrival_time_calendar=TimetableGenerator.arrival_time_calendar(8, 16),
        resource_calendars=[
            ResourceCalendar(
                id=TimetableGenerator.CALENDAR_ID,
                name=TimetableGenerator.CALENDAR_ID,
                time_periods=[
                    TimePeriod(
                        from_=DAY.MONDAY,
                        to=DAY.MONDAY,
                        begin_time="10:00:00",
                        end_time="12:00:00",
                    ),
                    TimePeriod(
                        from_=DAY.TUESDAY,
                        to=DAY.TUESDAY,
                        begin_time="10:00:00",
                        end_time="15:00:00",
                    ),
                    TimePeriod(
                        from_=DAY.WEDNESDAY,
                        to=DAY.SUNDAY,
                        begin_time="10:00:00",
                        end_time="12:00:00",
                    ),
                ],
            )
        ],
    )

    store = replace_constraints(
        store,
        batching_constraints=[
            ConstraintsGenerator.week_day_constraint(
                [TimetableGenerator.FIRST_ACTIVITY],
                allowed_days=[DAY.MONDAY, DAY.TUESDAY],
            )
        ],
    )

    input = SelfRatingInput.from_base_solution(store.solution)

    _, action = first_valid(
        store, AddDateTimeRuleByAvailabilityAction.rate_self(store, input)
    )

    assert action is not None
    assert isinstance(action, AddDateTimeRuleByAvailabilityAction)
    assert action.params["task_id"] == TimetableGenerator.FIRST_ACTIVITY
    assert action.params["time_period"] == TimePeriod.from_start_end(
        10, 15, DAY.TUESDAY
    )
