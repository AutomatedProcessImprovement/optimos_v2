from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import Literal

from o2.actions.base_actions.base_action import (
    BaseActionParamsType,
    RateSelfReturnType,
)
from o2.actions.base_actions.batching_rule_base_action import (
    BatchingRuleBaseAction,
)
from o2.models.constraints import RULE_TYPE
from o2.models.rule_selector import RuleSelector
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.state import State
from o2.models.timetable import (
    COMPARATOR,
    BatchingRule,
    FiringRule,
)
from o2.store import Store


class AddReadyLargeWTRuleBaseActionParamsType(BaseActionParamsType):
    """Parameter for AddReadyLargeWTRuleBaseAction."""

    task_id: str
    waiting_time: int
    type: Literal[RULE_TYPE.LARGE_WT, RULE_TYPE.READY_WT]


@dataclass(frozen=True)
class AddReadyLargeWTRuleBaseAction(BatchingRuleBaseAction, ABC, str=False):
    """AddReadyLargeWTRuleBaseAction will add a new day of week and time of day rule."""

    params: AddReadyLargeWTRuleBaseActionParamsType

    def apply(self, state: State, enable_prints: bool = True) -> State:
        """Create a copy of the timetable with the rule size modified."""
        """Apply the action to the state."""
        timetable = state.timetable
        task_id = self.params["task_id"]
        waiting_time = self.params["waiting_time"]
        type = self.params["type"]

        assert waiting_time <= 24 * 60 * 60, "Waiting time must be less than 24 hours"

        existing_task_rules = timetable.get_batching_rules_for_task(task_id)

        if not existing_task_rules:
            # TODO Also allow adding new rules
            # TODO 2: Allow combining rules, e.g. extending date range
            return state

        # Find the rule to modify
        rule = existing_task_rules[0]
        index = timetable.batch_processing.index(rule)

        new_or_rule = [
            FiringRule(
                attribute=type,
                comparison=COMPARATOR.GREATER_THEN_OR_EQUAL,
                value=waiting_time,
            ),
            # This is needed, or else we get an error
            FiringRule(
                attribute=type,
                comparison=COMPARATOR.LESS_THEN_OR_EQUAL,
                value=24 * 60 * 60,
            ),
        ]
        updated_rule = replace(
            rule,
            firing_rules=rule.firing_rules + [new_or_rule],
        )

        if enable_prints:
            print(f"\t\t>> Adding rule for {task_id} with large_wt >= {waiting_time}")

        return state.replace_timetable(
            batch_processing=timetable.batch_processing[:index]
            + [updated_rule]
            + timetable.batch_processing[index + 1 :],
        )

    @staticmethod
    @abstractmethod
    def rate_self(
        store: Store, input: SelfRatingInput
    ) -> RateSelfReturnType["AddReadyLargeWTRuleBaseAction"]:
        pass

    @staticmethod
    def get_default_rating() -> RATING:
        """Return the default rating for this action."""
        return RATING.MEDIUM
