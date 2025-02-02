from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

from dataclass_wizard import JSONWizard

if TYPE_CHECKING:
    from o2.models.state import State
    from o2.models.timetable import BatchingRule, FiringRule


@dataclass(frozen=True)
class RuleSelector(JSONWizard):
    """Rule selector for batching rule and firing rule."""

    batching_rule_task_id: str
    # OR Index, AND Index
    firing_rule_index: Optional[tuple[int, int]]

    @staticmethod
    def from_batching_rule(
        batching_rule: "BatchingRule",
        firing_rule_index: Optional[tuple[int, int]] = None,
    ) -> "RuleSelector":
        """Create a rule selector from a batching rule."""
        return RuleSelector(
            batching_rule_task_id=batching_rule.task_id,
            firing_rule_index=firing_rule_index,
        )

    @property
    def has_firing_rule(self) -> bool:
        """Check if the selector has a firing rule."""
        return self.firing_rule_index is not None

    def get_batching_rule_from_state(self, state: "State") -> Optional["BatchingRule"]:
        """Get a batching rule by rule selector."""
        return next(
            (
                rule
                for rule in state.timetable.batch_processing
                if rule.task_id == self.batching_rule_task_id
            ),
            None,
        )

    def get_firing_rule_from_state(self, state: "State") -> Optional["FiringRule"]:
        """Get a firing rule by rule selector."""
        if self.firing_rule_index is None:
            return None
        batching_rule = self.get_batching_rule_from_state(state)
        if batching_rule is None:
            return None
        return batching_rule.firing_rules[self.firing_rule_index[0]][
            self.firing_rule_index[1]
        ]

    def id(self):
        if self.firing_rule_index is None:
            return f"#{self.batching_rule_task_id}"
        return "#{}-{}-{}".format(
            self.batching_rule_task_id,
            self.firing_rule_index[0],
            self.firing_rule_index[1],
        )

    def __str__(self):
        if self.firing_rule_index is not None:
            return f"Batching Rule: {self.batching_rule_task_id}>{self.firing_rule_index[0]}>{self.firing_rule_index[1]}"
        return f"Batching Rule: {self.batching_rule_task_id}"
