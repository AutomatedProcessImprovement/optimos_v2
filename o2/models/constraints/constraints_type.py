from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, Union

from dataclass_wizard import JSONWizard

from o2.models.constraints.batching_constraints import BatchingConstraints
from o2.models.constraints.daily_hour_rule_constraints import (
    DailyHourRuleConstraints,
    is_daily_hour_constraint,
)
from o2.models.constraints.large_wt_rule_constraints import (
    LargeWtRuleConstraints,
    is_large_wt_constraint,
)
from o2.models.constraints.ready_wt_rule_constraints import (
    ReadyWtRuleConstraints,
    is_ready_wt_constraint,
)
from o2.models.constraints.size_rule_constraints import (
    SizeRuleConstraints,
    is_size_constraint,
)
from o2.models.constraints.week_day_rule_constraints import (
    WeekDayRuleConstraints,
    is_week_day_constraint,
)
from o2.models.legacy_constraints import ConstraintsResourcesItem, ResourceConstraints
from o2.util.helper import name_is_clone_of

if TYPE_CHECKING:
    from o2.models.timetable import TimetableType


@dataclass(frozen=True)
class ConstraintsType(JSONWizard):
    """Global Constraints Type including resource timetable and batching constraints."""

    # TODO: Add more constraints here
    batching_constraints: list[
        Union[
            SizeRuleConstraints,
            ReadyWtRuleConstraints,
            LargeWtRuleConstraints,
            WeekDayRuleConstraints,
            DailyHourRuleConstraints,
        ]
    ] = field(default_factory=list)
    # Legacy Optimos constraints
    resources: list[ConstraintsResourcesItem] = field(default_factory=list)
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

    class _(JSONWizard.Meta):  # noqa: N801
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
                resource_constraints.verify_timetable(timetable) for resource_constraints in self.resources
            )
        )

    def verify_batching_constraints(self, timetable: "TimetableType") -> bool:
        """Check if the timetable is valid against the batching constraints.

        Will check batching constraints for all firing rules.
        """
        return all(constraint.verify_timetable(timetable) for constraint in self.batching_constraints)

    def get_legacy_constraints_for_resource(self, resource_id: str) -> Optional[ResourceConstraints]:
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
        return [constraint for constraint in self.batching_constraints if task in constraint.tasks]

    def get_batching_size_rule_constraints(self, task_id: str) -> list[SizeRuleConstraints]:
        """Get the size rule constraints for a specific task."""
        return [
            constraint
            for constraint in self.batching_constraints
            if task_id in constraint.tasks and is_size_constraint(constraint)
        ]

    def get_batching_ready_wt_rule_constraints(self, task_id: str) -> list[ReadyWtRuleConstraints]:
        """Get the ready waiting time rule constraints for a specific task."""
        return [
            constraint
            for constraint in self.batching_constraints
            if task_id in constraint.tasks and is_ready_wt_constraint(constraint)
        ]

    def get_batching_large_wt_rule_constraints(self, task_id: str) -> list[LargeWtRuleConstraints]:
        """Get the large waiting time rule constraints for a specific task."""
        return [
            constraint
            for constraint in self.batching_constraints
            if task_id in constraint.tasks and is_large_wt_constraint(constraint)
        ]

    def get_week_day_rule_constraints(self, task_id: str) -> list[WeekDayRuleConstraints]:
        """Get the week day rule constraints for a specific task."""
        return [
            constraint
            for constraint in self.batching_constraints
            if task_id in constraint.tasks and is_week_day_constraint(constraint)
        ]

    def get_daily_hour_rule_constraints(self, task_id: str) -> list[DailyHourRuleConstraints]:
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

    def get_duration_fn_for_task(self, task_id: str) -> str:
        """Get the duration function for a specific task."""
        size_constraint = self.get_batching_size_rule_constraints(task_id)
        if not size_constraint:
            return "1"
        first_constraint = size_constraint[0]
        return first_constraint.duration_fn
