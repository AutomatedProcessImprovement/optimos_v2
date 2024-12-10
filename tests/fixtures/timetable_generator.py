import io
import xml.etree.ElementTree as ElementTree
from dataclasses import replace

from o2.models.constraints import BATCH_TYPE, RULE_TYPE
from o2.models.days import DAY
from o2.models.timetable import (
    COMPARATOR,
    DISTRIBUTION_TYPE,
    ArrivalTimeDistribution,
    BatchingRule,
    Distribution,
    DistributionParameter,
    EventDistribution,
    FiringRule,
    GatewayBranchingProbability,
    Probability,
    Resource,
    ResourceCalendar,
    ResourcePool,
    TaskResourceDistribution,
    TaskResourceDistributions,
    TimePeriod,
    TimetableType,
)


class TimetableGenerator:
    RESOURCE_ID = "BASE_RESOURCE"
    CALENDAR_ID = "BASE_CALENDAR"
    GATEWAY_ID = "OR_GATEWAY"

    FIRST_ACTIVITY = "FIRST_ACTIVITY"
    SECOND_ACTIVITY = "SECOND_ACTIVITY"
    THIRD_ACTIVITY = "THIRD_ACTIVITY"
    IN_LOOP_ACTIVITY = "IN_LOOP"
    LAST_ACTIVITY = "LAST_ACTIVITY"
    BATCHING_BASE_SIZE = 3

    def __init__(self, bpmn: str):
        fileIo = io.StringIO()
        fileIo.write(bpmn)
        fileIo.seek(0)
        self.bpmn = ElementTree.parse(fileIo)
        self.bpmnRoot = self.bpmn.getroot()
        # Get all the Elements of kind bpmn:task in bpmn:process
        self.tasks: list[ElementTree.Element] = self.bpmnRoot.findall(
            ".//{http://www.omg.org/spec/BPMN/20100524/MODEL}task"
        )
        self.task_ids = [task.attrib["id"] for task in self.tasks]
        self.timetable = TimetableType(
            resource_profiles=[],
            arrival_time_distribution=ArrivalTimeDistribution(
                distribution_name=DISTRIBUTION_TYPE.FIXED,
                distribution_params=[
                    DistributionParameter(value=0),
                ],
            ),
            gateway_branching_probabilities=[],
            batch_processing=[],
            arrival_time_calendar=[],
            task_resource_distribution=[],
            resource_calendars=[],
            event_distribution=EventDistribution(),
            total_cases=1000,
            start_time="2000-01-01T00:00:00Z",
        )

    def create_simple_resource_profile(self):
        """Create a simple resource profile with one resource.
        To be compatible with legacy Optimos, we we'll create one pool per task"""
        self.timetable = replace(
            self.timetable,
            resource_profiles=TimetableGenerator.resource_pools(self.task_ids),
        )
        return self

    def create_simple_arrival_time_calendar(
        self, start=0, end=23, include_end_hour=True
    ):
        self.timetable = replace(
            self.timetable,
            arrival_time_calendar=TimetableGenerator.arrival_time_calendar(
                start, end, include_end_hour=include_end_hour
            ),
        )
        return self

    def create_simple_arrival_time_distribution(self, min=60, max=60):
        self.timetable = replace(
            self.timetable,
            arrival_time_distribution=self.arrival_time_distribution(min, max),
        )
        return self

    def create_simple_task_resource_distribution(self, duration=60 * 60):
        self.timetable = replace(
            self.timetable,
            task_resource_distribution=TimetableGenerator.task_resource_distribution_simple(
                self.task_ids, duration
            ),
        )
        return self

    def create_simple_resource_calendars(self):
        self.timetable = replace(
            self.timetable,
            resource_calendars=TimetableGenerator.resource_calendars(0, 23, True),
        )
        return self

    def create_simple_gateway_branching_probabilities(self):
        self.timetable.gateway_branching_probabilities.append(
            GatewayBranchingProbability(
                gateway_id=self.GATEWAY_ID,
                probabilities=[
                    Probability(path_id="FLOW_OR_JOIN", value=0.9),
                    Probability(path_id="FLOW_OR_LAST", value=0.1),
                ],
            )
        )
        return self

    def create_simple_batch_processing(self, size=BATCHING_BASE_SIZE):
        self.timetable = replace(
            self.timetable,
            batch_processing=[
                self.batching_size_rule(task.attrib["id"], size) for task in self.tasks
            ],
        )
        return self

    @staticmethod
    def resource_calendars(
        begin_hour=9,
        end_hour=17,
        include_end_hour=False,
        only_week_days=False,
        include_extra_minute=False,
    ):
        return [
            ResourceCalendar(
                id=TimetableGenerator.CALENDAR_ID,
                name=TimetableGenerator.CALENDAR_ID,
                time_periods=[
                    TimePeriod(
                        from_=DAY.MONDAY,
                        to=DAY.SUNDAY if not only_week_days else DAY.FRIDAY,
                        begin_time=f"{begin_hour:02}:00:00",
                        end_time=f"{end_hour:02}:"
                        + (
                            "59:59"
                            if include_end_hour
                            else "00:00"
                            if not include_extra_minute
                            else "00:01"
                        ),
                    )
                ],
            )
        ]

    @staticmethod
    def resource_calendars_multi_resource(
        num_resources: int,
        begin_hour=9,
        end_hour=17,
        include_end_hour=False,
        only_week_days=False,
    ):
        return [
            ResourceCalendar(
                id=TimetableGenerator.CALENDAR_ID + "_" + str(i),
                name=TimetableGenerator.CALENDAR_ID + "_" + str(i),
                time_periods=[
                    TimePeriod(
                        from_=DAY.MONDAY,
                        to=DAY.SUNDAY if not only_week_days else DAY.FRIDAY,
                        begin_time=f"{begin_hour:02}:00:00",
                        end_time=f"{end_hour:02}:"
                        + ("59:59" if include_end_hour else "00:00"),
                    )
                ],
            )
            for i in range(1, num_resources + 1)
        ]

    @staticmethod
    def batching_size_rule(
        task_id: str,
        size: int = BATCHING_BASE_SIZE,
        duration_distribution=1.0,
    ):
        return BatchingRule(
            task_id=task_id,
            type=BATCH_TYPE.PARALLEL,
            size_distrib=[
                # Forbid execution of the task without batching
                Distribution(key=str(1), value=0.0),
                Distribution(key=str(size), value=1.0),
            ],
            duration_distrib=[Distribution(key=str(size), value=duration_distribution)],
            firing_rules=[
                [
                    FiringRule(
                        attribute=RULE_TYPE.SIZE,
                        comparison=COMPARATOR.EQUAL,
                        value=size,
                    )
                ]
            ],
        )

    @staticmethod
    def ready_wt_rule(
        task_id: str, ready_wt: int, size=BATCHING_BASE_SIZE, duration_distribution=1.0
    ):
        return BatchingRule(
            task_id=task_id,
            type=BATCH_TYPE.PARALLEL,
            size_distrib=[
                # Forbid execution of the task without batching
                Distribution(key=str(1), value=0.0),
                Distribution(key=str(size), value=1.0),
            ],
            duration_distrib=[
                Distribution(
                    key=str(size),
                    value=duration_distribution,
                )
            ],
            firing_rules=[
                [
                    FiringRule(
                        attribute=RULE_TYPE.READY_WT,
                        comparison=COMPARATOR.EQUAL,
                        value=ready_wt,
                    ),
                    # We need a size rule as well, also it must be last in the list
                    FiringRule(
                        attribute=RULE_TYPE.SIZE,
                        comparison=COMPARATOR.EQUAL,
                        value=size,
                    ),
                ],
            ],
        )

    @staticmethod
    def large_wt_rule(
        task_id: str,
        min_wt: int,
        size=BATCHING_BASE_SIZE,
        duration_distribution=1.0,
    ):
        return BatchingRule(
            task_id=task_id,
            type=BATCH_TYPE.PARALLEL,
            # Forbid execution of the task without batching
            size_distrib=[
                Distribution(key=str(1), value=0.0),
            ]
            + [
                Distribution(key=str(s), value=1 / (size - 1))
                for s in range(2, size + 1)
            ],
            duration_distrib=[
                Distribution(
                    key=str(s),
                    value=duration_distribution,
                )
                for s in range(1, size + 1)
            ],
            firing_rules=[
                [
                    FiringRule(
                        attribute=RULE_TYPE.LARGE_WT,
                        comparison=COMPARATOR.LESS_THEN_OR_EQUAL,
                        value=24 * 60 * 60,
                    ),
                    FiringRule(
                        attribute=RULE_TYPE.LARGE_WT,
                        comparison=COMPARATOR.GREATER_THEN_OR_EQUAL,
                        value=min_wt,
                    ),
                    FiringRule(
                        attribute=RULE_TYPE.SIZE,
                        comparison=COMPARATOR.EQUAL,
                        value=size,
                    ),
                ],
            ],
        )

    @staticmethod
    def week_day_rule(
        task_id: str,
        week_day: DAY = DAY.MONDAY,
        size=BATCHING_BASE_SIZE,
        include_monday=True,
        include_size=True,
    ):
        assert not (include_monday and not include_size)

        if include_monday:
            rules = [
                # This is a Dummy Rule! Because we need to have at least one valid rule for the first day of simulation
                # TODO: Speak about this with Orlenys about this
                [
                    FiringRule(
                        attribute=RULE_TYPE.WEEK_DAY,
                        comparison=COMPARATOR.EQUAL,
                        value=DAY.MONDAY,
                    )
                ],
                [
                    FiringRule(
                        attribute=RULE_TYPE.WEEK_DAY,
                        comparison=COMPARATOR.EQUAL,
                        value=week_day,
                    ),
                    FiringRule(
                        attribute=RULE_TYPE.SIZE,
                        comparison=COMPARATOR.EQUAL,
                        value=size,
                    ),
                ],
            ]
        elif include_size:
            rules = [
                [
                    FiringRule(
                        attribute=RULE_TYPE.WEEK_DAY,
                        comparison=COMPARATOR.EQUAL,
                        value=week_day,
                    ),
                    FiringRule(
                        attribute=RULE_TYPE.SIZE,
                        comparison=COMPARATOR.EQUAL,
                        value=size,
                    ),
                ]
            ]
        else:
            rules = [
                [
                    FiringRule(
                        attribute=RULE_TYPE.WEEK_DAY,
                        comparison=COMPARATOR.EQUAL,
                        value=week_day,
                    ),
                ]
            ]

        return BatchingRule(
            task_id=task_id,
            type=BATCH_TYPE.PARALLEL,
            size_distrib=[
                # Forbid execution of the task without batching
                Distribution(key=str(1), value=0.0),
                Distribution(key=str(size), value=1.0),
            ],
            duration_distrib=[
                Distribution(
                    key=str(size),
                    value=0.75,
                )
            ],
            firing_rules=rules,
        )

    @staticmethod
    def daily_hour_rule(
        task_id: str,
        min_hour: int,
        max_hour: int,
        size=BATCHING_BASE_SIZE,
        duration_distribution=1.0,
    ):
        return BatchingRule(
            task_id=task_id,
            type=BATCH_TYPE.PARALLEL,
            size_distrib=[
                # Forbid execution of the task without batching
                Distribution(key=str(1), value=0.0),
                Distribution(key=str(size), value=1.0),
            ],
            duration_distrib=[
                Distribution(
                    key=str(size),
                    value=duration_distribution,
                )
            ],
            firing_rules=[
                [
                    FiringRule(
                        attribute=RULE_TYPE.DAILY_HOUR,
                        comparison=COMPARATOR.GREATER_THEN_OR_EQUAL,
                        value=min_hour,
                    ),
                    FiringRule(
                        attribute=RULE_TYPE.DAILY_HOUR,
                        comparison=COMPARATOR.LESS_THEN_OR_EQUAL,
                        value=max_hour,
                    ),
                    # We need a size rule as well, also it must be last in the list
                    FiringRule(
                        attribute=RULE_TYPE.SIZE,
                        comparison=COMPARATOR.EQUAL,
                        value=size,
                    ),
                ],
            ],
        )

    @staticmethod
    def task_resource_distribution_simple(task_ids: list[str], duration=60 * 60):
        return [
            TaskResourceDistributions(
                task_id=task_id,
                resources=[
                    TaskResourceDistribution(
                        resource_id=TimetableGenerator.RESOURCE_ID,
                        distribution_name=DISTRIBUTION_TYPE.FIXED,
                        distribution_params=[DistributionParameter(value=duration)],
                    )
                ],
            )
            for task_id in task_ids
        ]

    @staticmethod
    def task_resource_distribution_multi_resource(
        task_ids: list[str], num_resources: int, duration=60 * 60
    ):
        return [
            TaskResourceDistributions(
                task_id=task_id,
                resources=[
                    TaskResourceDistribution(
                        resource_id=f"{TimetableGenerator.RESOURCE_ID}_{i}",
                        distribution_name=DISTRIBUTION_TYPE.FIXED,
                        distribution_params=[DistributionParameter(value=duration)],
                    )
                    for i in range(1, num_resources + 1)
                ],
            )
            for task_id in task_ids
        ]

    @staticmethod
    def resource_pools(task_ids: list[str], cost_per_hour: int = 1, fixed_cost_fn="0"):
        return [
            ResourcePool(
                id=task_id,
                name="Base Resource Pool",
                fixed_cost_fn=fixed_cost_fn,
                resource_list=[
                    Resource(
                        id=TimetableGenerator.RESOURCE_ID,
                        name=TimetableGenerator.RESOURCE_ID,
                        calendar=TimetableGenerator.CALENDAR_ID,
                        cost_per_hour=cost_per_hour,
                        amount=1,
                        assigned_tasks=[task_id for task_id in task_ids],
                    )
                ],
            )
            for task_id in task_ids
        ]

    @staticmethod
    def resource_pools_multi_resource(
        task_ids: list[str],
        num_resources: int,
        cost_per_hour: int = 1,
        fixed_cost_fn="0",
    ):
        return [
            ResourcePool(
                id=task_id,
                name="Base Resource Pool",
                fixed_cost_fn=fixed_cost_fn,
                resource_list=[
                    Resource(
                        id=f"{TimetableGenerator.RESOURCE_ID}_{i}",
                        name=f"{TimetableGenerator.RESOURCE_ID}_{i}",
                        calendar=f"{TimetableGenerator.CALENDAR_ID}_{i}",
                        cost_per_hour=cost_per_hour,
                        amount=1,
                        assigned_tasks=[task_id for task_id in task_ids],
                    )
                    for i in range(1, num_resources + 1)
                ],
            )
            for task_id in task_ids
        ]

    @staticmethod
    def arrival_time_distribution(min=60, max=60):
        return (
            ArrivalTimeDistribution(
                distribution_name=DISTRIBUTION_TYPE.FIXED,
                distribution_params=[
                    DistributionParameter(value=min),
                ],
            )
            if min == max
            else ArrivalTimeDistribution(
                distribution_name=DISTRIBUTION_TYPE.UNIFORM,
                distribution_params=[
                    DistributionParameter(value=min),
                    DistributionParameter(value=max),
                ],
            )
        )

    @staticmethod
    def arrival_time_calendar(
        start=9,
        end=17,
        include_end_hour=False,
        include_extra_minute=False,
        only_week_days=False,
        days=None,
    ):
        if days is not None:
            return [
                TimePeriod(
                    from_=day,
                    to=day,
                    begin_time=f"{start:02}:00:00",
                    end_time=f"{end:02}:" + ("59:59" if include_end_hour else "00:00"),
                )
                for day in days
            ]
        return [
            TimePeriod(
                from_=DAY.MONDAY,
                to=DAY.SUNDAY if not only_week_days else DAY.FRIDAY,
                begin_time=f"{start:02}:00:00",
                end_time=f"{end:02}:"
                + (
                    "59:59"
                    if include_end_hour
                    else "00:00"
                    if not include_extra_minute
                    else "00:01"
                ),
            )
        ]

    def generate_simple(self, include_batching=False):
        self.create_simple_resource_profile()
        self.create_simple_arrival_time_calendar()
        # Create an event on avg. every 10 minutes
        self.create_simple_arrival_time_distribution(min=5 * 60, max=15 * 60)
        self.create_simple_task_resource_distribution()
        self.create_simple_resource_calendars()
        self.create_simple_gateway_branching_probabilities()
        if include_batching:
            self.create_simple_batch_processing()
        return self.timetable
