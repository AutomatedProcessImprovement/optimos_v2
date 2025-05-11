from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeGuard

from dataclass_wizard import JSONWizard

from o2.models.constraints.batching_constraints import BatchingConstraints
from o2.models.days import DAY
from o2.models.timetable import BATCH_TYPE, RULE_TYPE, FiringRule

if TYPE_CHECKING:
    from o2.models.timetable import TimetableType


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

    def allowed_hours_for_day(self, day: DAY) -> list[int]:
        """Get the allowed hours for a specific day."""
        return self.allowed_hours.get(day, [])

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


def is_daily_hour_constraint(
    val: BatchingConstraints,
) -> TypeGuard[DailyHourRuleConstraints]:
    """Check if the constraint is a daily hour constraint."""
    return val.rule_type == RULE_TYPE.DAILY_HOUR
