from dataclasses import dataclass, field, replace
from enum import Enum
from typing import TYPE_CHECKING, List, TypeGuard, Union

from dataclass_wizard import JSONWizard

from o2.models.days import DAY
from o2.models.legacy_constraints import ConstraintsResourcesItem

if TYPE_CHECKING:
    from o2.models.timetable import TimetableType


class BATCH_TYPE(str, Enum):
    SEQUENTIAL = "Sequential"  # one after another
    CONCURRENT = "Concurrent"  # tasks are in progress simultaneously
    # (executor changes the context between different tasks)
    PARALLEL = "Parallel"  # tasks are being executed simultaneously


class RULE_TYPE(str, Enum):
    READY_WT = "ready_wt"
    LARGE_WT = "large_wt"
    DAILY_HOUR = "daily_hour"
    WEEK_DAY = "week_day"
    SIZE = "size"


@dataclass(frozen=True)
class BatchingConstraints(JSONWizard):
    id: str
    tasks: list[str]
    batch_type: BATCH_TYPE
    rule_type: RULE_TYPE


@dataclass(frozen=True)
class SizeRuleConstraints(BatchingConstraints, JSONWizard):
    duration_fn: str
    min_size: int
    max_size: int

    class _(JSONWizard.Meta):
        key_transform_with_dump = "SNAKE"
        tag = RULE_TYPE.SIZE.value
        tag_key = "rule_type"


@dataclass(frozen=True)
class ReadyWtRuleConstraints(BatchingConstraints, JSONWizard):
    min_wt: int
    max_wt: int

    class _(JSONWizard.Meta):
        key_transform_with_dump = "SNAKE"
        tag = RULE_TYPE.READY_WT.value
        tag_key = "rule_type"


@dataclass(frozen=True)
class LargeWtRuleConstraints(BatchingConstraints, JSONWizard):
    min_wt: int
    max_wt: int

    class _(JSONWizard.Meta):
        key_transform_with_dump = "SNAKE"
        tag = RULE_TYPE.LARGE_WT.value
        tag_key = "rule_type"


@dataclass(frozen=True)
class WeekDayRuleConstraints(BatchingConstraints, JSONWizard):
    allowed_days: list[DAY]

    class _(JSONWizard.Meta):
        key_transform_with_dump = "SNAKE"
        tag = RULE_TYPE.LARGE_WT.value
        tag_key = "rule_type"


@dataclass(frozen=True)
class DailyHourRuleConstraints(BatchingConstraints, JSONWizard):
    allowed_hours: list[int]

    class _(JSONWizard.Meta):
        key_transform_with_dump = "SNAKE"
        tag = RULE_TYPE.DAILY_HOUR.value
        tag_key = "rule_type"


def is_size_constraint(val: BatchingConstraints) -> TypeGuard[SizeRuleConstraints]:
    return val.rule_type == RULE_TYPE.SIZE


def is_ready_wt_constraint(
    val: BatchingConstraints,
) -> TypeGuard[ReadyWtRuleConstraints]:
    return val.rule_type == RULE_TYPE.READY_WT


def is_large_wt_constraint(
    val: BatchingConstraints,
) -> TypeGuard[LargeWtRuleConstraints]:
    return val.rule_type == RULE_TYPE.LARGE_WT


def is_week_day_constraint(
    val: BatchingConstraints,
) -> TypeGuard[WeekDayRuleConstraints]:
    return val.rule_type == RULE_TYPE.WEEK_DAY


def is_daily_hour_constraint(
    val: BatchingConstraints,
) -> TypeGuard[DailyHourRuleConstraints]:
    return val.rule_type == RULE_TYPE.DAILY_HOUR


@dataclass(frozen=True)
class ConstraintsType(JSONWizard):
    # TODO: Add more constraints here
    batching_constraints: List[
        Union[
            SizeRuleConstraints,
            ReadyWtRuleConstraints,
            LargeWtRuleConstraints,
            WeekDayRuleConstraints,
            DailyHourRuleConstraints,
        ]
    ] = field(default_factory=list)
    # Legacy Optimos constraints
    resources: List[ConstraintsResourcesItem] = field(default_factory=list)
    """Legacy Optimos Constraint: Resource Constraints"""
    max_cap: int = 9999999
    """Legacy Optimos Constraint: Max number of hours a resource can work in a week"""
    max_shift_size: int = 24
    """Legacy Optimos Constraint: Max number of hours in a continuous shift block"""
    max_shift_blocks: int = 24
    """Legacy Optimos Constraint: Max number of continuos shift block in a day"""
    hours_in_day: int = 24
    """Legacy Optimos Constraint: Hours/Slots per day"""
    time_var: int = 60
    """Legacy Optimos Constraint: Slot duration in minutes"""

    class _(JSONWizard.Meta):
        key_transform_with_dump = "SNAKE"

    def verify_legacy_constraints(self, timetable: "TimetableType") -> bool:
        """Check if the timetable is valid against the constraints.

        Will check resource constraints for all resources as well as the base constraints.
        """
        return (
            timetable.max_total_hours_per_resource <= self.max_cap
            and timetable.max_consecutive_hours_per_resource <= self.max_shift_size
            and timetable.max_periods_per_day_per_resource <= self.max_shift_blocks
            and all(
                resource_constraints.verify_timetable(timetable)
                for resource_constraints in self.resources
            )
        )

    def get_batching_constraints_for_task(self, task: str) -> list[BatchingConstraints]:
        return [
            constraint
            for constraint in self.batching_constraints
            if task in constraint.tasks
        ]

    def get_batching_size_rule_constraints(
        self, task_id: str
    ) -> list[SizeRuleConstraints]:
        return [
            constraint
            for constraint in self.batching_constraints
            if task_id in constraint.tasks and is_size_constraint(constraint)
        ]

    def get_batching_ready_wt_rule_constraints(
        self, task_id: str
    ) -> list[ReadyWtRuleConstraints]:
        return [
            constraint
            for constraint in self.batching_constraints
            if task_id in constraint.tasks and is_ready_wt_constraint(constraint)
        ]

    def get_batching_large_wt_rule_constraints(
        self, task_id: str
    ) -> list[LargeWtRuleConstraints]:
        return [
            constraint
            for constraint in self.batching_constraints
            if task_id in constraint.tasks and is_large_wt_constraint(constraint)
        ]

    def get_week_day_rule_constraints(
        self, task_id: str
    ) -> list[WeekDayRuleConstraints]:
        return [
            constraint
            for constraint in self.batching_constraints
            if task_id in constraint.tasks and is_week_day_constraint(constraint)
        ]

    def get_daily_hour_rule_constraints(
        self, task_id: str
    ) -> list[DailyHourRuleConstraints]:
        return [
            constraint
            for constraint in self.batching_constraints
            if task_id in constraint.tasks and is_daily_hour_constraint(constraint)
        ]

    class _(JSONWizard.Meta):
        key_transform_with_dump = "SNAKE"
        tag_key = "rule_type"
