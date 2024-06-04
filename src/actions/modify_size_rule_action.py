from sympy import Symbol, lambdify
from optimos_v2.src.actions.base_action import BaseAction, BaseActionParamsType
from optimos_v2.src.types.state import State
from optimos_v2.src.types.timetable import BatchingRule, Distribution, FiringRule


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
        new_size = int(oldRule.size_distrib[0].key) + self.params["size_increment"]
        fn = lambdify(Symbol("size"), self.params["duration_fn"])
        size_distrib = [
            Distribution(
                key=str(new_size),
                value=1,
            )
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
                    attribute="size",
                    comparison="=",
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
