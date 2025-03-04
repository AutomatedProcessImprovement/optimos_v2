from os import path

from o2.models.constraints import ConstraintsType, SizeRuleConstraints
from o2.models.days import DAY
from o2.models.state import State
from o2.models.time_period import TimePeriod
from o2.models.timetable import (
    BATCH_TYPE,
    DISTRIBUTION_TYPE,
    RULE_TYPE,
    ArrivalTimeDistribution,
    DistributionParameter,
    GatewayBranchingProbability,
    Probability,
    Resource,
    ResourceCalendar,
    ResourcePool,
    TaskResourceDistribution,
    TaskResourceDistributions,
    TimetableType,
)
from o2.store import Store

FIXED_COST_FN = "1 * 1/size"
COST_FN = "1"
DURATION_FN = "1/size"

CLERKS = ["Clerk_1", "Clerk_2", "Clerk_3", "Clerk_4"]

CLERK_TASKS = [
    "TASK_CHECK_CREDIT_HISTORY",
    "TASK_CHECK_INCOME_SOURCES",
    "TASK_ASSESS_APPLICATION",
    "TASK_MAKE_CREDIT_OFFER",
    "TASK_NOTIFY_REJECTION",
    "TASK_RECIEVE_CUSTOMER_FEEDBACK",
]

OFFICER_TASKS = ["TASK_ASSESS_APPLICATION"]


def create_timetable():
    return TimetableType(
        resource_profiles=[
            ResourcePool(
                id=task_id,
                name=f"{task_id} Resource Pool",
                fixed_cost_fn=FIXED_COST_FN,
                resource_list=[
                    Resource(
                        id=resource_id,
                        name=resource_id,
                        calendar=f"{resource_id}timetable",
                        cost_per_hour=10,
                        amount=1,
                        assigned_tasks=[task_id for task_id in CLERK_TASKS],
                    )
                    for resource_id in CLERKS
                ],
            )
            for task_id in CLERK_TASKS
        ]
        + [
            ResourcePool(
                id="Credit_Officer_1",
                name="Credit_Officer_1 Resource Pool",
                fixed_cost_fn=FIXED_COST_FN,
                resource_list=[
                    Resource(
                        id="Credit_Officer_1",
                        name="Credit_Officer_1",
                        calendar="Credit_Officer_1timetable",
                        cost_per_hour=10,
                        amount=1,
                        assigned_tasks=[task_id for task_id in OFFICER_TASKS],
                    )
                ],
            )
        ],
        arrival_time_distribution=ArrivalTimeDistribution(
            distribution_name=DISTRIBUTION_TYPE.UNIFORM,
            distribution_params=[
                DistributionParameter(value=30),
                DistributionParameter(value=600),
            ],
        ),
        gateway_branching_probabilities=[
            GatewayBranchingProbability(
                gateway_id="GATEWAY_CUSTOMER_FEEDBACK",
                probabilities=[
                    Probability(
                        path_id="sid-AFEC7074-8C12-43E2-A1FE-87D5CEF395C8", value=0.2
                    ),
                    Probability(
                        path_id="sid-AE313010-5715-438C-AD61-1C02F03DCF77", value=0.8
                    ),
                ],
            ),
            GatewayBranchingProbability(
                gateway_id="GATEWAY_LENDING_DECISION",
                probabilities=[
                    Probability(
                        path_id="sid-8AE82A7B-75EE-401B-8ABE-279FB05A3946", value=0.2
                    ),
                    Probability(
                        path_id="sid-789335C6-205C-4A03-9AD6-9655893C1FFB", value=0.8
                    ),
                ],
            ),
        ],
        batch_processing=[],
        arrival_time_calendar=[
            TimePeriod.from_start_end(9, 13, DAY.MONDAY),
            TimePeriod.from_start_end(9, 13, DAY.TUESDAY),
            TimePeriod.from_start_end(9, 13, DAY.WEDNESDAY),
            TimePeriod.from_start_end(9, 13, DAY.THURSDAY),
            TimePeriod.from_start_end(9, 13, DAY.FRIDAY),
        ],
        task_resource_distribution=[
            TaskResourceDistributions(
                task_id=task_id,
                resources=[
                    TaskResourceDistribution(
                        resource_id=resource_id,
                        distribution_name=DISTRIBUTION_TYPE.FIXED,
                        distribution_params=[DistributionParameter(value=300)],
                    )
                    for resource_id in CLERKS
                ],
            )
            for task_id in CLERK_TASKS
        ]
        + [
            TaskResourceDistributions(
                task_id="TASK_ASSESS_APPLICATION",
                resources=[
                    TaskResourceDistribution(
                        resource_id="Credit_Officer_1",
                        distribution_name=DISTRIBUTION_TYPE.FIXED,
                        distribution_params=[DistributionParameter(value=3600)],
                    )
                ],
            )
        ],
        resource_calendars=[
            ResourceCalendar(
                id=f"{resource_id}timetable",
                name=f"{resource_id}timetable",
                time_periods=[
                    TimePeriod.from_start_end(9, 17, DAY.MONDAY),
                    TimePeriod.from_start_end(9, 17, DAY.TUESDAY),
                    TimePeriod.from_start_end(9, 17, DAY.WEDNESDAY),
                    TimePeriod.from_start_end(9, 17, DAY.THURSDAY),
                ],
            )
            for resource_id in CLERKS
        ]
        + [
            ResourceCalendar(
                id="Credit_Officer_1timetable",
                name="Credit_Officer_1timetable",
                time_periods=[
                    TimePeriod.from_start_end(14, 17, DAY.MONDAY),
                    TimePeriod.from_start_end(14, 17, DAY.TUESDAY),
                    TimePeriod.from_start_end(14, 17, DAY.WEDNESDAY),
                    TimePeriod.from_start_end(14, 17, DAY.THURSDAY),
                    TimePeriod.from_start_end(14, 17, DAY.FRIDAY),
                ],
            )
        ],
        total_cases=1000,
        start_time="2000-01-01T00:00:00Z",
    )


def create_constraints():
    return ConstraintsType(
        batching_constraints=[
            SizeRuleConstraints(
                id=f"size_rule_{task_id}",
                tasks=[task_id],
                batch_type=BATCH_TYPE.PARALLEL,
                rule_type=RULE_TYPE.SIZE,
                duration_fn=DURATION_FN,
                cost_fn=COST_FN,
                min_size=1,
                max_size=10,
            )
            for task_id in (CLERK_TASKS + OFFICER_TASKS)
        ],
    )


current_file_path = __file__
bpmn_file_name = "demo_model.bpmn"
with open(path.join(path.dirname(current_file_path), bpmn_file_name)) as f:
    bpmn_definition = f.read()

timetable = create_timetable()
constraints = create_constraints()

initial_state = State(
    bpmn_definition=bpmn_definition,
    timetable=timetable,
)
demo_store = Store.from_state_and_constraints(
    initial_state,
    constraints,
)
