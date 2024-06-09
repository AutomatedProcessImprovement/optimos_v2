from dataclasses import replace
from o2.actions.base_action import BaseAction, BaseActionParamsType
from o2.types.state import State
from o2.types.timetable import COMPARATOR, BatchingRule, Distribution, FiringRule
from o2.types.constraints import RULE_TYPE


class ModifyReadyWtRuleActionParamsType(BaseActionParamsType):
    rule_hash: str
    wt_increment: int


class ModifyReadyWtRuleAction(BaseAction):
    params: ModifyReadyWtRuleActionParamsType

    # Returns a copy of the timetable with the rule size modified
    def apply(self, state: State, enable_prints=True):
        timetable = state.timetable
        ruleHash = self.params["rule_hash"]
        wt_increment = self.params["wt_increment"]

        (ruleIndex, oldRule) = next(
            (i, rule)
            for i, rule in enumerate(timetable.batch_processing)
            if rule.id() == ruleHash
        )

        old_wt = int(self.get_dominant_distribution(oldRule).key)
        new_wt = old_wt + wt_increment

        firing_rules = [
            [
                FiringRule(
                    attribute=RULE_TYPE.READY_WT,
                    comparison=COMPARATOR.EQUAL,
                    value=new_wt,
                )
            ]
        ]
        newRule = replace(
            oldRule,
            firing_rules=firing_rules,
        )

        if enable_prints:
            print(f"\t\t>> Modifying rule {oldRule.id()} to new ready_wt = {new_wt}")

        return state.replaceTimetable(
            batch_processing=timetable.batch_processing[:ruleIndex]
            + [newRule]
            + timetable.batch_processing[ruleIndex + 1 :],
        )

    def get_dominant_distribution(self, oldRule: BatchingRule):
        # Find the size distribution with the highest probability
        return max(
            oldRule.size_distrib,
            key=lambda distribution: distribution.value,
        )
