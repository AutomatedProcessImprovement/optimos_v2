from o2.actions.base_actions.base_action import (
    BaseAction,
    BaseActionParamsType,
    RateSelfReturnType,
)
from o2.actions.base_actions.modify_size_rule_base_action import (
    ModifySizeRuleAction,
    ModifySizeRuleBaseActionParamsType,
)
from o2.models.rule_selector import RuleSelector
from o2.models.self_rating import SelfRatingInput
from o2.models.state import State
from o2.models.timetable import (
    BATCH_TYPE,
    COMPARATOR,
    RULE_TYPE,
    BatchingRule,
    Distribution,
    FiringRule,
    rule_is_size,
)
from o2.store import Store


class ModifySizeOfSignificantRuleActionParamsType(BaseActionParamsType):
    """Parameter for ModifySizeOfSignificantRuleAction."""

    task_id: str
    change_size: int
    """How much to change the size of the rule by; positive for increase, negative for decrease."""


class ModifySizeOfSignificantRuleAction(BaseAction):
    """ModifySizeOfSignificantRuleAction will modify the size of the most significant BatchingRule."""

    params: ModifySizeOfSignificantRuleActionParamsType

    def apply(self, state: State, enable_prints: bool = True) -> State:
        """Apply the action to the state."""
        timetable = state.timetable
        task_id = self.params["task_id"]
        change_size = self.params["change_size"]

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
                        significant_rule = RuleSelector.from_batching_rule(
                            batching_rule, (i, 0)
                        )
                        significant_size = size

        # If no significant rule is found, add a new one
        if significant_rule is None:
            # TODO: We need to find the min size from the constraints
            new_size = 1 + abs(change_size)
            new_batching_rule = BatchingRule.from_task_id(
                task_id=task_id,
                size=new_size,
                firing_rules=[
                    FiringRule(
                        attribute=RULE_TYPE.SIZE,
                        comparison=COMPARATOR.GREATER_THEN_OR_EQUAL,
                        value=new_size,
                    )
                ],
            )
            return state.replace_timetable(
                batch_processing=timetable.batch_processing + [new_batching_rule]
            )

        return ModifySizeRuleAction(
            ModifySizeRuleBaseActionParamsType(
                rule=significant_rule,
                size_increment=change_size,
                # TODO: Get from constraints
                duration_fn="0.8*size",
            )
        ).apply(state, enable_prints=enable_prints)

    @staticmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        """Generate a best set of parameters & self-evaluates this action."""
        raise NotImplementedError("Not implemented")
