from typing import Literal

from typing_extensions import Required, override

from o2.actions.base_actions.base_action import (
    BaseAction,
    BaseActionParamsType,
    RateSelfReturnType,
)
from o2.models.rule_selector import RuleSelector
from o2.models.solution import Solution
from o2.models.state import State
from o2.models.timetable import (
    RULE_TYPE,
    BatchingRule,
    FiringRule,
)
from o2.store import Store


class ModifyLargeReadyWtOfSignificantRuleActionParamsType(BaseActionParamsType):
    """Parameter for ModifyLargeReadyWtOfSignificantRuleAction."""

    task_id: Required[str]
    type: Required[Literal[RULE_TYPE.LARGE_WT, RULE_TYPE.READY_WT]]
    change_wt: Required[int]
    """How much to change the wt of the rule by; positive for increase, negative for decrease."""
    duration_fn: Required[str]


class ModifyLargeReadyWtOfSignificantRuleAction(BaseAction):
    """ModifyLargeReadyWtOfSignificantRuleAction will modify the size of the most significant BatchingRule."""

    params: ModifyLargeReadyWtOfSignificantRuleActionParamsType

    @override
    def apply(self, state: State, enable_prints: bool = True) -> State:
        timetable = state.timetable
        task_id = self.params["task_id"]
        change_wt = self.params["change_wt"]
        duration_fn = self.params.get("duration_fn", None)
        firing_rule_type = self.params["type"]

        batching_rules = timetable.get_batching_rules_for_task(task_id)

        # Smallest wt (only) and-rule (if change_size > 0)
        # Largest wt (only) and-rule (if change_size < 0)
        significant_rule = None
        significant_wt = float("inf") if change_wt > 0 else -float("inf")

        for batching_rule in batching_rules:
            for i, and_rules in enumerate(batching_rule.firing_rules):
                if len(and_rules) > 1 or len(and_rules) == 0:
                    continue
                firing_rule = and_rules[0]
                if (
                    firing_rule.attribute == firing_rule_type
                    # TODO: We should also support lte
                    and firing_rule.is_gt_or_gte
                ):
                    wt = int(firing_rule.value) // 3600
                    new_wt = wt + change_wt
                    if new_wt < 1 or new_wt > 23:
                        continue
                    if change_wt > 0 and wt < significant_wt or change_wt < 0 and wt > significant_wt:
                        significant_rule = RuleSelector.from_batching_rule(batching_rule, (i, 0))
                        significant_wt = wt
        # If no significant rule is found, add a new one
        if significant_rule is None:
            batching_rule = BatchingRule.from_task_id(
                task_id,
                firing_rules=[
                    FiringRule.gte(firing_rule_type, abs(change_wt) * 3600),
                    FiringRule.lte(firing_rule_type, 24 * 60 * 60),
                ],
                duration_fn=duration_fn,
            )
            return state.replace_timetable(batch_processing=timetable.batch_processing + [batching_rule])
        else:
            timetable = timetable.replace_firing_rule(
                rule_selector=significant_rule,
                new_firing_rule=FiringRule.gte(firing_rule_type, (significant_wt + change_wt) * 3600),
            )
            return state.replace_timetable(timetable=timetable)

    @override
    @staticmethod
    def rate_self(store: Store, input: Solution) -> RateSelfReturnType:
        raise NotImplementedError("Not implemented")
