from o2.actions.base_action import BaseAction, BaseActionParamsType
from o2.types.state import State
from o2.actions.batching_rule_action import (
    BatchingRuleAction,
    BatchingRuleActionParamsType,
)

# TODO: Implement Me!


class AddRuleActionParamsType(BatchingRuleActionParamsType):
    pass


class AddRuleAction(BatchingRuleAction):
    def __init__(self, params: AddRuleActionParamsType):
        self.rule = params

    # Returns a copy of the timetable with the rule added
    def apply(self, state: State, enable_prints=True):
        raise NotImplementedError
