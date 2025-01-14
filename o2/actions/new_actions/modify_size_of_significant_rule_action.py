from dataclasses import replace

from o2.actions.base_actions.base_action import (
    BaseAction,
    BaseActionParamsType,
    RateSelfReturnType,
)
from o2.models.rule_selector import RuleSelector
from o2.models.self_rating import SelfRatingInput
from o2.models.state import State
from o2.models.timetable import COMPARATOR, RULE_TYPE, FiringRule, rule_is_size
from o2.store import Store


class ModifySizeOfSignificantRuleActionParamsType(BaseActionParamsType):
    """Parameter for ModifySizeOfSignificantRuleAction."""

    task_id: str
    change_size: int
    """How much to change the size of the rule by; positive for increase, negative for decrease."""


class ModifySizeOfSignificantRuleAction(BaseAction):
    """ModifySizeOfSignificantRuleAction will modify the size of the most significant BatchingRule."""

    params: ModifySizeOfSignificantRuleActionParamsType

    def apply(self, state: State, enable_prints: bool = True) -> State:
        timetable = state.timetable
        task_id = self.params["task_id"]
        change_size = self.params["change_size"]

        batching_rules = timetable.get_batching_rules_for_task(task_id)
        if len(batching_rules) == 0:
            return state

        # Smallest size (only) and-rule (if change_size > 0)
        # Largest size (only) and-rule (if change_size < 0)
        significant_rule = None
        significant_size = 0

        for batching_rule in batching_rules:
            for i, and_rules in enumerate(batching_rule.firing_rules):
                if len(and_rules) > 1:
                    continue
                if rule_is_size(and_rules[0]):
                    size = int(and_rules[0].value)
                    if change_size > 0 and size < significant_size:
                        significant_rule = RuleSelector.from_batching_rule(
                            batching_rule, (i, 0)
                        )
                        significant_size = size
                    elif change_size < 0 and size > significant_size:
                        significant_rule = RuleSelector.from_batching_rule(
                            batching_rule, (i, 0)
                        )
                        significant_size = size

        if significant_rule is None:
            return state

        batching_rule = significant_rule.get_batching_rule_from_state(state)
        assert batching_rule is not None
        firing_rule = batching_rule.get_firing_rule(significant_rule)
        assert firing_rule is not None
        new_batching_rule = batching_rule.replace_firing_rule(
            significant_rule,
            FiringRule(
                attribute=RULE_TYPE.SIZE,
                comparison=COMPARATOR.EQUAL,
                value=firing_rule.value + change_size,
            ),
        )

        return replace(
            state,
            timetable=timetable.replace_batching_rule(
                significant_rule, new_batching_rule
            ),
        )

    @staticmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        raise NotImplementedError("Not implemented")
