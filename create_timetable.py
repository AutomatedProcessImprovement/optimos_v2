from o2.models.state import State
from tests.fixtures.store_fixture import ONE_TASK_BPMN_PATH
from tests.fixtures.timetable_generator import TimetableGenerator

bpmn_content = open(ONE_TASK_BPMN_PATH).read()
state = State(
    bpmn_definition=bpmn_content,
    timetable=TimetableGenerator(bpmn_content).generate_simple(),
    for_testing=True,
)

state = state.replace_timetable(
    # Resource has cost of $10/h
    resource_profiles=TimetableGenerator.resource_pools(
        [TimetableGenerator.FIRST_ACTIVITY], 10, fixed_cost_fn="15"
    ),
    # Working one case takes 1h
    task_resource_distribution=TimetableGenerator.task_resource_distribution_simple(
        [TimetableGenerator.FIRST_ACTIVITY], 1 * 60 * 60
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
        TimetableGenerator.batching_size_rule(
            TimetableGenerator.FIRST_ACTIVITY, 4, duration_distribution=0.5
        )
    ],
    total_cases=8,
)

print(state.timetable.to_json())
