from typing import TypedDict
from src.types.constraints import ConstraintsType
from src.types.state import State
from src.types.timetable import BatchingRule, Distribution, FiringRule, TimetableType
from dataclasses import dataclass, replace
from sympy import Symbol, lambdify


class BaseActionParamsType(TypedDict):
    pass


@dataclass(frozen=True)
class Action:
    params: BaseActionParamsType

    def apply(self, state: State, enable_prints=True) -> State:
        raise NotImplementedError

    def __str__(self):
        return f"{self.__class__.__name__}({self.params})"

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.params == other.params


class RemoveRuleActionParamsType(BaseActionParamsType):
    rule_hash: str


class RemoveRuleAction(Action):
    params: RemoveRuleActionParamsType

    # Returns a copy of the timetable with the rule removed
    # (TimetableType is a frozen dataclass)
    def apply(self, state: State, enable_prints=True):
        timetable = state.timetable
        rule_hash = self.params["rule_hash"]

        rule_index = next(
            (
                i
                for i, rule in enumerate(timetable.batch_processing)
                if rule.id() == rule_hash
            ),
            None,
        )
        if rule_index is None:
            print(f"Rule with hash {rule_hash} not found")
            return state
        if enable_prints:
            print(f"\t\t>> Removing rule {rule_hash}")
        return state.replaceTimetable(
            batch_processing=timetable.batch_processing[:rule_index]
            + timetable.batch_processing[rule_index + 1 :],
        )


class AddRuleActionParamsType(BaseActionParamsType):
    pass


class AddRuleAction(Action):
    def __init__(self, params: AddRuleActionParamsType):
        self.rule = params

    # Returns a copy of the timetable with the rule added
    def apply(self, state: State, enable_prints=True):
        raise NotImplementedError


class ModifySizeRuleActionParamsType(BaseActionParamsType):
    rule_hash: str
    size_increment: int
    duration_fn: str


class ModifySizeRuleAction(Action):
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
