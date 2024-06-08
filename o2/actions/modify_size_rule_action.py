from sympy import Symbol, lambdify
from o2.actions.base_action import BaseAction, BaseActionParamsType
from o2.types.state import State
from o2.types.timetable import COMPARATOR, BatchingRule, Distribution, FiringRule
from optimos_v2.o2.types.constraints import RULE_TYPE


class ModifySizeRuleActionParamsType(BaseActionParamsType):
    rule_hash: str
    size_increment: int
    duration_fn: str


class ModifySizeRuleAction(BaseAction):
    params: ModifySizeRuleActionParamsType

    # Returns a copy of the timetable with the rule size modified
    def apply(self, state: State, enable_prints=True):
        timetable = state.timetable
        ruleHash = self.params["rule_hash"]

        (ruleIndex, oldRule) = next(
            (i, rule)
            for i, rule in enumerate(timetable.batch_processing)
            if rule.id() == ruleHash
        )
        old_size = self.get_dominant_distribution(oldRule).key
        new_size = int(old_size) + self.params["size_increment"]
        fn = lambdify(Symbol("size"), self.params["duration_fn"])
        size_distrib = [
            Distribution(
                key=str(1),
                value=0,
            ),
            Distribution(
                key=str(new_size),
                value=1,
            ),
        ]
        duration_distrib = [
            Distribution(
                key=str(new_size),
                value=fn(new_size),
            )
        ]

        firing_rules = [
            [
                FiringRule(
                    attribute=RULE_TYPE.SIZE,
                    comparison=COMPARATOR.EQUAL,
                    value=new_size,
                )
            ]
        ]
        newRule = BatchingRule(
            task_id=oldRule.task_id,
            type=oldRule.type,
            size_distrib=size_distrib,
            duration_distrib=duration_distrib,
            firing_rules=firing_rules,
        )

        if enable_prints:
            print(
                f"\t\t>> Modifying rule {oldRule.id()} to new size = {new_size} & duration_modifier = {fn(new_size)}"
            )

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
