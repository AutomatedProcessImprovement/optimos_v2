from o2.actions.base_action import BaseAction, BaseActionParamsType
from o2.types.state import State


class AddRuleActionParamsType(BaseActionParamsType):
    pass


class AddRuleAction(BaseAction):
    def __init__(self, params: AddRuleActionParamsType):
        self.rule = params

    # Returns a copy of the timetable with the rule added
    def apply(self, state: State, enable_prints=True):
        raise NotImplementedError

