from dataclasses import dataclass
from typing import Optional

from o2.types.timetable import BatchingRule
from o2.types.state import State


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

    def get_batching_rule_from_state(self, state: State):
        return next(
            rule
            for rule in state.timetable.batch_processing
            if rule.task_id == self.batching_rule_task_id
        )

    def get_firing_rule_from_state(self, state: State):
        if self.firing_rule_index is None:
            return None
        batching_rule = self.get_batching_rule_from_state(state)
        return batching_rule.firing_rules[self.firing_rule_index[0]][
            self.firing_rule_index[1]
        ]

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
            return f"Batching Rule: {self.batching_rule_task_id}>{self.firing_rule_index[0]}>{self.firing_rule_index[1]}"
        return f"Batching Rule: {self.batching_rule_task_id}"
