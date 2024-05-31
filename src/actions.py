from typing import TypedDict
from src.types.constraints import ConstraintsType
from src.types.state import State
from src.types.timetable import BatchingRule, Distribution, FiringRule, TimetableType
from dataclasses import replace
from sympy import Symbol, lambdify


class Action:
    def __init__(self, params):
        self.params = params

    def apply(self, state: State) -> State:
        raise NotImplementedError

    def __str__(self):
        return f"{self.__class__.__name__}({self.params})"

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.params == other.params


class RemoveRuleActionParamsType(TypedDict):
    rule_index: int


class RemoveRuleAction(Action):
    def __init__(self, params: RemoveRuleActionParamsType):
        self.params = params

    # Returns a copy of the timetable with the rule removed
    # (TimetableType is a frozen dataclass)
    def apply(self, state: State):
        timetable = state.timetable
        return state.replaceTimetable(
            batch_processing=timetable.batch_processing[: self.params["rule_index"]]
            + timetable.batch_processing[self.params["rule_index"] + 1 :],
        )


class AddRuleActionParamsType(TypedDict):
    rule_index: int


class AddRuleAction(Action):
    def __init__(self, params: AddRuleActionParamsType):
        self.rule = params

    # Returns a copy of the timetable with the rule added
    def apply(self, state: State):
        timetable = state.timetable
        return state.replaceTimetable(
            rules=timetable.batch_processing[: self.params["rule_index"]]
            + [self.rule]
            + timetable.batch_processing[self.params["rule_index"] :],
        )


class ModifySizeRuleActionParamsType(TypedDict):
    rule_index: int
    size_increment: int
    duration_fn: str


class ModifySizeRuleAction(Action):
    def __init__(self, params: ModifySizeRuleActionParamsType):
        self.params = params

    # Returns a copy of the timetable with the rule size modified
    def apply(self, state: State):
        timetable = state.timetable
        oldRule = timetable.batch_processing[self.params["rule_index"]]
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

        return state.replaceTimetable(
            batch_processing=timetable.batch_processing[: self.params["rule_index"]]
            + [newRule]
            + timetable.batch_processing[self.params["rule_index"] + 1 :],
        )
