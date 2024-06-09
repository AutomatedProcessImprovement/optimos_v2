from dataclasses import dataclass
from typing import Optional

from o2.types.timetable import BatchingRule


@dataclass(frozen=True)
class RuleSelector:
    batching_rule_task_id: str
    # OR Index, AND Index
    firing_rule_index: Optional[tuple[int, int]]

    @staticmethod
    def from_batching_rule(
        batching_rule: BatchingRule, firing_rule_index: Optional[tuple[int, int]]
    ):
        return RuleSelector(
            batching_rule_task_id=batching_rule.task_id,
            firing_rule_index=firing_rule_index,
        )

    @property
    def has_firing_rule(self):
        return self.firing_rule_index is not None

    def id(self):
        if self.firing_rule_index is None:
            return "#{}".format(self.batching_rule_task_id)
        return "#{}-{}-{}".format(
            self.batching_rule_task_id,
            self.firing_rule_index[0],
            self.firing_rule_index[1],
        )

    def __str__(self):
        if self.firing_rule_index is not None:
            return f"Batching Rule: {self.batching_rule_task_id} > {self.firing_rule_index[0]} > {self.firing_rule_index[1]})"
        return f"Batching Rule: {self.batching_rule_task_id}"
