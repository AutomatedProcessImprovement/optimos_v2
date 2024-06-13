from dataclasses import dataclass
from enum import Enum
from typing import List, TypeGuard, Union
from dataclass_wizard import JSONWizard

from o2.types.days import DAY


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


@dataclass(frozen=True)
class ConstraintsType(JSONWizard):
    # TODO: Add more constraints here
    batching_constraints: List[
        Union[
            SizeRuleConstraints,
            ReadyWtRuleConstraints,
            LargeWtRuleConstraints,
            WeekDayRuleConstraints,
        ]
    ]

    class _(JSONWizard.Meta):
        key_transform_with_dump = "SNAKE"

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

    class _(JSONWizard.Meta):
        key_transform_with_dump = "SNAKE"
        tag_key = "rule_type"
