from o2.actions.base_action import BaseAction, BaseActionParamsType, RateSelfReturnType
from o2.actions.modify_size_rule_base_action import (
    ModifySizeRuleBaseAction,
    ModifySizeRuleBaseActionParamsType,
)
from o2.models.self_rating import SelfRatingInput
from o2.store import Store


class ModifySizeRuleByWTActionParamsType(ModifySizeRuleBaseActionParamsType):
    """Parameter for ModifySizeRuleByWTAction."""

    pass


class ModifySizeRuleByWTAction(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on waiting time."""

    params: ModifySizeRuleByWTActionParamsType

    @staticmethod
    def rate_self(store: "Store", input: SelfRatingInput) -> RateSelfReturnType:
        """Generate a best set of parameters & self-evaluates this action."""
        for task_id in store.base_state.timetable.tasks:
            task = store.base_state.timetable.tasks[task_id]
            if task.waiting_time is not None:
                return {
                    "rule": task_id,
                    "size_increment": 1,
                    "duration_fn": "size",
                }
