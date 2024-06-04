from dataclasses import dataclass
from enum import Enum
from typing import List, TypedDict, Union
from dataclass_wizard import JSONWizard


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
    duration_fn: str

@dataclass(frozen=True)
class SizeRuleConstraints(BatchingConstraints, JSONWizard):
    min_size: int
    max_size: int

    class _(JSONWizard.Meta):
        key_transform_with_dump = "SNAKE"
        tag = RULE_TYPE.SIZE.value
        tag_key = "rule_type"


@dataclass(frozen=True)
class ConstraintsType(JSONWizard):
    # TODO: Add more constraints here
    batching_constraints: list[SizeRuleConstraints]

    class _(JSONWizard.Meta):
        key_transform_with_dump = "SNAKE"

    def get_batching_constraints_for_task(self, task: str) -> list[BatchingConstraints]:
        return [
            constraint
            for constraint in self.batching_constraints
            if task in constraint.tasks
        ]
