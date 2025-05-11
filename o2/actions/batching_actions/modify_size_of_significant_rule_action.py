from typing_extensions import Required, override

from o2.actions.base_actions.base_action import (
    BaseAction,
    BaseActionParamsType,
    RateSelfReturnType,
)
from o2.actions.base_actions.modify_size_rule_base_action import (
    ModifySizeRuleAction,
    ModifySizeRuleBaseActionParamsType,
)
from o2.models.evaluation import Evaluation
from o2.models.rule_selector import RuleSelector
from o2.models.solution import Solution
from o2.models.state import State
from o2.models.timetable import (
    RULE_TYPE,
    BatchingRule,
    FiringRule,
    rule_is_size,
)
from o2.store import Store


class ModifySizeOfSignificantRuleActionParamsType(BaseActionParamsType):
    """Parameter for ModifySizeOfSignificantRuleAction."""

    task_id: Required[str]
    change_size: Required[int]
    """How much to change the size of the rule by; positive for increase, negative for decrease."""
    duration_fn: Required[str]


class ModifySizeOfSignificantRuleAction(BaseAction):
    """ModifySizeOfSignificantRuleAction will modify the size of the most significant BatchingRule."""

    params: ModifySizeOfSignificantRuleActionParamsType

    @override
    def apply(self, state: State, enable_prints: bool = True) -> State:
        timetable = state.timetable
        task_id = self.params["task_id"]
        change_size = self.params["change_size"]
        duration_fn = self.params.get("duration_fn", None)

        batching_rules = timetable.get_batching_rules_for_task(task_id)

        # Smallest size (only) and-rule (if change_size > 0)
        # Largest size (only) and-rule (if change_size < 0)
        significant_rule = None
        significant_size = float("inf") if change_size > 0 else -float("inf")

        for batching_rule in batching_rules:
            for i, and_rules in enumerate(batching_rule.firing_rules):
                if len(and_rules) > 1 or len(and_rules) == 0:
                    continue
                firing_rule = and_rules[0]
                if rule_is_size(firing_rule):
                    size = int(firing_rule.value)
                    new_size = size + change_size
                    if new_size < 1:
                        continue
                    if (
                        change_size > 0
                        and size < significant_size
                        or change_size < 0
                        and size > significant_size
                    ):
                        significant_rule = RuleSelector.from_batching_rule(batching_rule, (i, 0))
                        significant_size = size

        # If no significant rule is found, add a new one
        if significant_rule is None:
            # TODO: We need to find the min size from the constraints
            new_size = min(max(1 + change_size, 1), 2)
            new_batching_rule = BatchingRule.from_task_id(
                task_id=task_id,
                firing_rules=[FiringRule.gte(RULE_TYPE.SIZE, new_size)],
                duration_fn=duration_fn,
            )
            return state.replace_timetable(batch_processing=timetable.batch_processing + [new_batching_rule])

        return ModifySizeRuleAction(
            ModifySizeRuleBaseActionParamsType(
                rule=significant_rule,
                size_increment=change_size,
                duration_fn=duration_fn,
            )
        ).apply(state, enable_prints=enable_prints)

    @override
    @staticmethod
    def rate_self(store: Store, input: Solution) -> RateSelfReturnType:
        raise NotImplementedError("Not implemented")
