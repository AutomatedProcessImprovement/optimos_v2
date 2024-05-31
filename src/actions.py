from typing import TypedDict
from src.types.constraints import ConstraintsType
from src.types.state import State
from src.types.timetable import TimetableType
from dataclasses import replace


class Action:
    def __init__(self, params):
        self.params = params

    def apply(self, state: State):
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
