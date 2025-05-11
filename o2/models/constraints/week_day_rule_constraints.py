from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeGuard

from dataclass_wizard import JSONWizard

from o2.models.constraints.batching_constraints import BatchingConstraints
from o2.models.days import DAY
from o2.models.timetable import RULE_TYPE, FiringRule

if TYPE_CHECKING:
    from o2.models.timetable import TimetableType


@dataclass(frozen=True)
class WeekDayRuleConstraints(BatchingConstraints, JSONWizard):
    """Week day rule constraints for batching."""

    allowed_days: list[DAY]

    class _(JSONWizard.Meta):  # noqa: N801
        key_transform_with_dump = "SNAKE"
        tag = RULE_TYPE.WEEK_DAY.value
        tag_key = "rule_type"

    def verify_timetable(self, timetable: "TimetableType") -> bool:
        """Check if the timetable is valid against the constraints."""
        rules: list[FiringRule[DAY]] = timetable.get_firing_rules_for_tasks(
            self.tasks, rule_type=RULE_TYPE.WEEK_DAY, batch_type=self.batch_type
        )
        return all(self._verify_firing_rule(rule) for rule in rules)

    def _verify_firing_rule(self, firing_rule: FiringRule[DAY]) -> bool:
        """Check if the firing rule is valid against the constraints."""
        return firing_rule.value in self.allowed_days


def is_week_day_constraint(
    val: BatchingConstraints,
) -> TypeGuard[WeekDayRuleConstraints]:
    """Check if the constraint is a week day constraint."""
    return val.rule_type == RULE_TYPE.WEEK_DAY
