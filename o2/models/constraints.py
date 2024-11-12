from abc import ABC, abstractmethod
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import TYPE_CHECKING, List, Optional, TypeGuard, Union

from dataclass_wizard import JSONWizard
from sympy import Symbol, lambdify

from o2.models.days import DAY
from o2.models.legacy_constraints import ConstraintsResourcesItem, ResourceConstraints
from o2.models.timetable import BATCH_TYPE, COMPARATOR, RULE_TYPE, FiringRule
from o2.util.helper import name_is_clone_of

if TYPE_CHECKING:
    from o2.models.timetable import TimetableType


@dataclass(frozen=True)
class BatchingConstraints(JSONWizard, ABC):
    """Base class for all batching constraints."""

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
    """Size rule constraints for batching."""

    duration_fn: str
    cost_fn: str
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
    """Ready waiting time rule constraints for batching."""

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
    """Large waiting time rule constraints for batching."""

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
    """Week day rule constraints for batching."""

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
    """Daily hour rule constraints for batching."""

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
        return True

    @staticmethod
    def allow_all(
        tasks: list[str], batch_type: BATCH_TYPE = BATCH_TYPE.PARALLEL
    ) -> "DailyHourRuleConstraints":
        """Create a daily hour rule constraint that allows all hours."""
        return DailyHourRuleConstraints(
            id="allow_all",
            tasks=tasks,
            batch_type=BATCH_TYPE.PARALLEL,
            rule_type=RULE_TYPE.DAILY_HOUR,
            allowed_hours={day: list(range(24)) for day in DAY},
        )


def is_size_constraint(val: BatchingConstraints) -> TypeGuard[SizeRuleConstraints]:
    """Check if the constraint is a size constraint."""
    return val.rule_type == RULE_TYPE.SIZE


def is_ready_wt_constraint(
    val: BatchingConstraints,
) -> TypeGuard[ReadyWtRuleConstraints]:
    """Check if the constraint is a ready waiting time constraint."""
    return val.rule_type == RULE_TYPE.READY_WT


def is_large_wt_constraint(
    val: BatchingConstraints,
) -> TypeGuard[LargeWtRuleConstraints]:
    """Check if the constraint is a large waiting time constraint."""
    return val.rule_type == RULE_TYPE.LARGE_WT


def is_week_day_constraint(
    val: BatchingConstraints,
) -> TypeGuard[WeekDayRuleConstraints]:
    """Check if the constraint is a week day constraint."""
    return val.rule_type == RULE_TYPE.WEEK_DAY


def is_daily_hour_constraint(
    val: BatchingConstraints,
) -> TypeGuard[DailyHourRuleConstraints]:
    """Check if the constraint is a daily hour constraint."""
    return val.rule_type == RULE_TYPE.DAILY_HOUR


@dataclass(frozen=True)
class ConstraintsType(JSONWizard):
    """Global Constraints Type including resource timetable and batching constraints."""

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
        tag_key = "rule_type"

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
        """Get the batching constraints for a specific task."""
        return [
            constraint
            for constraint in self.batching_constraints
            if task in constraint.tasks
        ]

    def get_batching_size_rule_constraints(
        self, task_id: str
    ) -> list[SizeRuleConstraints]:
        """Get the size rule constraints for a specific task."""
        return [
            constraint
            for constraint in self.batching_constraints
            if task_id in constraint.tasks and is_size_constraint(constraint)
        ]

    def get_batching_ready_wt_rule_constraints(
        self, task_id: str
    ) -> list[ReadyWtRuleConstraints]:
        """Get the ready waiting time rule constraints for a specific task."""
        return [
            constraint
            for constraint in self.batching_constraints
            if task_id in constraint.tasks and is_ready_wt_constraint(constraint)
        ]

    def get_batching_large_wt_rule_constraints(
        self, task_id: str
    ) -> list[LargeWtRuleConstraints]:
        """Get the large waiting time rule constraints for a specific task."""
        return [
            constraint
            for constraint in self.batching_constraints
            if task_id in constraint.tasks and is_large_wt_constraint(constraint)
        ]

    def get_week_day_rule_constraints(
        self, task_id: str
    ) -> list[WeekDayRuleConstraints]:
        """Get the week day rule constraints for a specific task."""
        return [
            constraint
            for constraint in self.batching_constraints
            if task_id in constraint.tasks and is_week_day_constraint(constraint)
        ]

    def get_daily_hour_rule_constraints(
        self, task_id: str
    ) -> list[DailyHourRuleConstraints]:
        """Get the daily hour rule constraints for a specific task."""
        return [
            constraint
            for constraint in self.batching_constraints
            if task_id in constraint.tasks and is_daily_hour_constraint(constraint)
        ]

    def get_fixed_cost_fn_for_task(self, task_id: str) -> str:
        """Get the fixed cost function for a specific task."""
        size_constraint = self.get_batching_size_rule_constraints(task_id)
        if not size_constraint:
            return "0"
        first_constraint = size_constraint[0]
        return first_constraint.cost_fn
