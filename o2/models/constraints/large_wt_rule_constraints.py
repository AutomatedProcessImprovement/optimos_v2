from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, TypeGuard

from dataclass_wizard import JSONWizard

from o2.models.constraints.batching_constraints import BatchingConstraints
from o2.models.timetable import RULE_TYPE, FiringRule

if TYPE_CHECKING:
    from o2.models.timetable import TimetableType


@dataclass(frozen=True)
class LargeWtRuleConstraints(BatchingConstraints, JSONWizard):
    """Large waiting time rule constraints for batching."""

    min_wt: Optional[int]
    max_wt: Optional[int]

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
        # TODO: We need to do checking in firing_rule pairs

        # # Special case: If the rule is a <(=) min wt, it is invalid if min wt is set
        # if (
        #     self.min_wt
        #     and self.min_wt > 0
        #     and (
        #         firing_rule.comparison == COMPARATOR.LESS_THEN
        #         or firing_rule.comparison == COMPARATOR.LESS_THEN_OR_EQUAL
        #     )
        # ):
        #     return False

        # # Special case: If the rule is a >(=) max wt, it is invalid if max wt is set
        # if self.max_wt and (
        #     firing_rule.comparison == COMPARATOR.GREATER_THEN
        #     or firing_rule.comparison == COMPARATOR.GREATER_THEN_OR_EQUAL
        # ):
        #     return False

        if (self.min_wt and firing_rule.value < self.min_wt) or (
            self.max_wt and firing_rule.value > self.max_wt
        ):
            return False

        return True


def is_large_wt_constraint(
    val: BatchingConstraints,
) -> TypeGuard[LargeWtRuleConstraints]:
    """Check if the constraint is a large waiting time constraint."""
    return val.rule_type == RULE_TYPE.LARGE_WT
