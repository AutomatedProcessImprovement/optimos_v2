from o2.models.days import DAY
from o2.models.state import State
from o2.models.time_period import TimePeriod
from o2.models.timetable import (
    BATCH_TYPE,
    RULE_TYPE,
    BatchingRule,
    Distribution,
    FiringRule,
)
from tests.fixtures.store_fixture import TWO_TASKS_BPMN_PATH
from tests.fixtures.timetable_generator import TimetableGenerator

bpmn_content = open(TWO_TASKS_BPMN_PATH).read()
state = State(
    bpmn_definition=bpmn_content,
    timetable=TimetableGenerator(bpmn_content).generate_simple(),
    for_testing=True,
)

time_period = TimePeriod.from_start_end(10, 15, DAY.FRIDAY)

state = state.replace_timetable(
    # Resource has cost of $10/h
    resource_profiles=TimetableGenerator.resource_pools(
        [TimetableGenerator.FIRST_ACTIVITY, TimetableGenerator.SECOND_ACTIVITY],
        10,
        fixed_cost_fn="15",
    ),
    # Working one case takes 1h
    task_resource_distribution=TimetableGenerator.task_resource_distribution_simple(
        [TimetableGenerator.FIRST_ACTIVITY, TimetableGenerator.SECOND_ACTIVITY],
        1 * 60 * 60,
    ),
    # Work from 9 to 18 (9h)
    resource_calendars=TimetableGenerator.resource_calendars(
        9, 18, include_end_hour=False, only_week_days=True
    ),
    # One Case every 24h
    arrival_time_distribution=TimetableGenerator.arrival_time_distribution(
        24 * 60 * 60,
        24 * 60 * 60,
    ),
    # Cases from 9:00 to 10:00
    arrival_time_calendar=TimetableGenerator.arrival_time_calendar(
        9, 10, include_end_hour=False, only_week_days=False
    ),
    # Batch Size of 4 (Meaning 4 days are needed to for a single batch)
    # Will work twice as fast, e.g. only needed 2 hours for 4 tasks
    batch_processing=[
        BatchingRule(
            task_id=TimetableGenerator.SECOND_ACTIVITY,
            type=BATCH_TYPE.PARALLEL,
            size_distrib=[Distribution(key=str(1), value=0.0)]
            + [
                Distribution(key=str(new_size), value=1.0) for new_size in range(2, 100)
            ],
            duration_distrib=[
                Distribution(key=str(new_size), value=1 / new_size)
                for new_size in range(1, 100)
            ],
            firing_rules=[
                [
                    FiringRule.eq(RULE_TYPE.WEEK_DAY, time_period.from_),
                    FiringRule.gte(RULE_TYPE.DAILY_HOUR, time_period.begin_time_hour),
                    FiringRule.lt(RULE_TYPE.DAILY_HOUR, time_period.end_time_hour),
                ],
            ],
        )
    ],
    total_cases=8,
)

print(state.timetable.to_json())
