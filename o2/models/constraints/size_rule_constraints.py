from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Optional, TypeGuard

from dataclass_wizard import JSONWizard
from sympy import Symbol, lambdify

from o2.models.constraints.batching_constraints import BatchingConstraints
from o2.models.timetable import RULE_TYPE, FiringRule

if TYPE_CHECKING:
    from o2.models.timetable import TimetableType


@dataclass(frozen=True)
class SizeRuleConstraints(BatchingConstraints, JSONWizard):
    """Size rule constraints for batching."""

    duration_fn: str
    cost_fn: str
    min_size: Optional[int]
    max_size: Optional[int]

    class _(JSONWizard.Meta):  # noqa: N801
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
        # Special case: Size 0 is always invalid
        if firing_rule.value == 0:
            from o2.util.logger import warn

            warn("Warning: Size 0 rule was created!")
            return False

        # Special case: If the rule is a <(=) min size, it is invalid if min size is set
        if self.min_size and self.min_size > 0 and (firing_rule.is_lt_or_lte):
            return False

        # Special case: If the rule is a >(=) max size, it is invalid if max size is set
        # TODO: Think about this
        # if self.max_size and (firing_rule.is_gt_or_gte):
        #     return False

        if (self.min_size and firing_rule.value < self.min_size) or (  # noqa: SIM103
            self.max_size and firing_rule.value > self.max_size
        ):
            return False

        return True

    @property
    def cost_fn_lambda(self) -> Callable[[float], float]:
        """Get the cost function as a lambda function."""
        return lambdify(Symbol("size"), self.cost_fn)

    @property
    def duration_fn_lambda(self) -> Callable[[float], float]:
        """Get the duration function as a lambda function."""
        return lambdify(Symbol("size"), self.duration_fn)


def is_size_constraint(val: BatchingConstraints) -> TypeGuard[SizeRuleConstraints]:
    """Check if the constraint is a size constraint."""
    return val.rule_type == RULE_TYPE.SIZE
