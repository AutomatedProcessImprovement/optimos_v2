from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import TYPE_CHECKING, List, Optional, TypeGuard, Union

from dataclass_wizard import JSONWizard

from o2.models.days import DAY
from o2.models.legacy_constraints import ConstraintsResourcesItem, ResourceConstraints
from o2.models.timetable import COMPARATOR, FiringRule
from o2.util.helper import name_is_clone_of

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
class BatchingConstraints(JSONWizard, ABC):
    id: str
    tasks: list[str]
    batch_type: BATCH_TYPE
    rule_type: RULE_TYPE

    @abstractmethod
    def verify_timetable(self, timetable: "TimetableType") -> bool:
        """Check if the timetable is valid against the constraints."""
        pass


@dataclass(frozen=True)
class SizeRuleConstraints(BatchingConstraints, JSONWizard):
    duration_fn: str
    min_size: Optional[int]
    max_size: Optional[int]

    class _(JSONWizard.Meta):
        key_transform_with_dump = "SNAKE"
        tag = RULE_TYPE.SIZE.value
        tag_key = "rule_type"

    def verify_timetable(self, timetable: "TimetableType") -> bool:
        """Check if the timetable is valid against the constraints."""
        rules: list[FiringRule[int]] = timetable.get_firing_rules_for_tasks(
            self.tasks, rule_type=RULE_TYPE.SIZE, batch_type=self.batch_type
        )
        return all(self._verify_firing_rule(rule) for rule in rules)

    def _verify_firing_rule(self, firing_rule: FiringRule[int]) -> bool:
        """Check if the firing rule is valid against the constraints."""
        # Special case: If the rule is a <(=) min size, it is invalid if min size is set
        if (
            self.min_size
            and self.min_size > 0
            and (
                firing_rule.comparison == COMPARATOR.LESS_THEN
                or firing_rule.comparison == COMPARATOR.LESS_THEN_OR_EQUAL
            )
        ):
            return False

        # Special case: If the rule is a >(=) max size, it is invalid if max size is set
        if self.max_size and (
            firing_rule.comparison == COMPARATOR.GREATER_THEN
            or firing_rule.comparison == COMPARATOR.GREATER_THEN_OR_EQUAL
        ):
            return False

        if (self.min_size and firing_rule.value < self.min_size) or (
            self.max_size and firing_rule.value > self.max_size
        ):
            return False

        return True


@dataclass(frozen=True)
class ReadyWtRuleConstraints(BatchingConstraints, JSONWizard):
    min_wt: int
    max_wt: int

    class _(JSONWizard.Meta):
        key_transform_with_dump = "SNAKE"
        tag = RULE_TYPE.READY_WT.value
        tag_key = "rule_type"

    def verify_timetable(self, timetable: "TimetableType") -> bool:
        """Check if the timetable is valid against the constraints."""
        rules: list[FiringRule[int]] = timetable.get_firing_rules_for_tasks(
            self.tasks, rule_type=RULE_TYPE.READY_WT, batch_type=self.batch_type
        )
        return all(self._verify_firing_rule(rule) for rule in rules)

    def _verify_firing_rule(self, firing_rule: FiringRule[int]) -> bool:
        """Check if the firing rule is valid against the constraints."""
        # Special case: If the rule is a <(=) min wt, it is invalid if min wt is set
        if (
            self.min_wt
            and self.min_wt > 0
            and (
                firing_rule.comparison == COMPARATOR.LESS_THEN
                or firing_rule.comparison == COMPARATOR.LESS_THEN_OR_EQUAL
            )
        ):
            return False

        # Special case: If the rule is a >(=) max wt, it is invalid if max wt is set
        if self.max_wt and (
            firing_rule.comparison == COMPARATOR.GREATER_THEN
            or firing_rule.comparison == COMPARATOR.GREATER_THEN_OR_EQUAL
        ):
            return False

        if (self.min_wt and firing_rule.value < self.min_wt) or (
            self.max_wt and firing_rule.value > self.max_wt
        ):
            return False

        return True


@dataclass(frozen=True)
class LargeWtRuleConstraints(BatchingConstraints, JSONWizard):
    min_wt: int
    max_wt: int

    class _(JSONWizard.Meta):
        key_transform_with_dump = "SNAKE"
        tag = RULE_TYPE.LARGE_WT.value
        tag_key = "rule_type"

    def verify_timetable(self, timetable: "TimetableType") -> bool:
        """Check if the timetable is valid against the constraints."""
        rules: list[FiringRule[int]] = timetable.get_firing_rules_for_tasks(
            self.tasks, rule_type=RULE_TYPE.LARGE_WT, batch_type=self.batch_type
        )
        return all(self._verify_firing_rule(rule) for rule in rules)

    def _verify_firing_rule(self, firing_rule: FiringRule[int]) -> bool:
        """Check if the firing rule is valid against the constraints."""
        # Special case: If the rule is a <(=) min wt, it is invalid if min wt is set
        if (
            self.min_wt
            and self.min_wt > 0
            and (
                firing_rule.comparison == COMPARATOR.LESS_THEN
                or firing_rule.comparison == COMPARATOR.LESS_THEN_OR_EQUAL
            )
        ):
            return False

        # Special case: If the rule is a >(=) max wt, it is invalid if max wt is set
        if self.max_wt and (
            firing_rule.comparison == COMPARATOR.GREATER_THEN
            or firing_rule.comparison == COMPARATOR.GREATER_THEN_OR_EQUAL
        ):
            return False

        if (self.min_wt and firing_rule.value < self.min_wt) or (
            self.max_wt and firing_rule.value > self.max_wt
        ):
            return False

        return True


@dataclass(frozen=True)
class WeekDayRuleConstraints(BatchingConstraints, JSONWizard):
    allowed_days: list[DAY]

    class _(JSONWizard.Meta):
        key_transform_with_dump = "SNAKE"
        tag = RULE_TYPE.LARGE_WT.value
        tag_key = "rule_type"

    def verify_timetable(self, timetable: "TimetableType") -> bool:
        """Check if the timetable is valid against the constraints."""
        rules: list[FiringRule[DAY]] = timetable.get_firing_rules_for_tasks(
            self.tasks, rule_type=RULE_TYPE.WEEK_DAY, batch_type=self.batch_type
        )
        return all(self._verify_firing_rule(rule) for rule in rules)

    def _verify_firing_rule(self, firing_rule: FiringRule[DAY]) -> bool:
        """Check if the firing rule is valid against the constraints."""
        return all(day in self.allowed_days for day in firing_rule.value)


@dataclass(frozen=True)
class DailyHourRuleConstraints(BatchingConstraints, JSONWizard):
    allowed_hours: dict[DAY, list[int]]

    class _(JSONWizard.Meta):
        key_transform_with_dump = "SNAKE"
        tag = RULE_TYPE.DAILY_HOUR.value
        tag_key = "rule_type"

    def verify_timetable(self, timetable: "TimetableType") -> bool:
        """Check if the timetable is valid against the constraints."""
        rules: list[FiringRule[int]] = timetable.get_firing_rules_for_tasks(
            self.tasks, rule_type=RULE_TYPE.DAILY_HOUR, batch_type=self.batch_type
        )
        return all(self._verify_firing_rule(rule) for rule in rules)

    def _verify_firing_rule(self, firing_rule: FiringRule[int]) -> bool:
        """Check if the firing rule is valid against the constraints."""
        # TODO: Implement this
        pass


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

    def verify_batching_constraints(self, timetable: "TimetableType") -> bool:
        """Check if the timetable is valid against the batching constraints.

        Will check batching constraints for all firing rules.
        """
        return all(
            constraint.verify_timetable(timetable)
            for constraint in self.batching_constraints
        )

    def get_legacy_constraints_for_resource(
        self, resource_id: str
    ) -> Optional[ResourceConstraints]:
        """Get the legacy constraints for a specific resource."""
        return next(
            (
                constraint.constraints
                for constraint in self.resources
                if (
                    constraint.id == resource_id
                    or constraint.id == (resource_id + "timetable")
                    or name_is_clone_of(resource_id, constraint.id)
                )
            ),
            None,
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
