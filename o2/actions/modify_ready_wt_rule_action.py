from dataclasses import dataclass
from typing import Literal

from o2.actions.base_actions.base_action import (
    BaseAction,
    BaseActionParamsType,
    RateSelfReturnType,
)
from o2.actions.batching_rule_action import (
    BatchingRuleAction,
    BatchingRuleActionParamsType,
)
from o2.models.constraints import RULE_TYPE
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.state import State
from o2.models.timetable import (
    COMPARATOR,
    FiringRule,
    rule_is_ready_wt,
)
from o2.store import Store

SIZE_OF_CHANGE = 100


@dataclass
class ModifyReadyWtRuleActionParamsType(BatchingRuleActionParamsType):
    """Parameter for `ModifyReadyWtRuleAction`."""

    wt_increment: int


@dataclass(frozen=True)
class ModifyReadyWtRuleAction(BatchingRuleAction, str=False):
    """`ModifyReadyWtRuleAction` will modify the `READY_WT` value of a `FiringRule`."""

    params: ModifyReadyWtRuleActionParamsType

    def apply(self, state: State, enable_prints: bool = True) -> State:
        """Apply the action to the state."""
        timetable = state.timetable
        rule_selector = self.params["rule"]
        wt_increment = self.params["wt_increment"]

        index, rule = timetable.get_batching_rule(rule_selector)
        if rule is None or index is None:
            print(f"BatchingRule not found for {rule_selector}")
            return state

        firing_rule = rule.get_firing_rule(rule_selector)
        if not rule_is_ready_wt(firing_rule):
            print(f"Firing rule not found for {rule_selector}")
            return state

        old_wt = firing_rule.value
        new_wt = old_wt + wt_increment

        new_firing_rule = FiringRule(
            attribute=RULE_TYPE.READY_WT,
            comparison=COMPARATOR.EQUAL,
            value=new_wt,
        )

        new_batching_rule = rule.replace_firing_rule(rule_selector, new_firing_rule)

        return state.replace_timetable(
            batch_processing=timetable.batch_processing[:index]
            + [new_batching_rule]
            + timetable.batch_processing[index + 1 :],
        )

    @staticmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        """Generate a best set of parameters & self-evaluates this action."""
        rule_selector = input.most_impactful_rule
        base_evaluation = store.current_evaluation
        if rule_selector is None:
            return

        firing_rule = rule_selector.get_firing_rule_from_state(store.base_state)

        if not rule_is_ready_wt(firing_rule):
            return

        base_max_waiting_time = base_evaluation.get_max_waiting_time_of_task_id(
            rule_selector.batching_rule_task_id
        )

        # Waiting time was always smaller than the rule
        if base_max_waiting_time < firing_rule.value:
            return

        constraints = store.constraints.get_batching_ready_wt_rule_constraints(
            rule_selector.batching_rule_task_id
        )

        max_allowed_min_size = max(
            [constraint.min_wt for constraint in constraints], default=0
        )

        # Decrementing the size would break the constraints
        if (firing_rule.value - SIZE_OF_CHANGE) < max_allowed_min_size:
            return

        yield (
            RATING.MEDIUM,
            ModifyReadyWtRuleAction(
                ModifyReadyWtRuleActionParamsType(
                    wt_increment=-1 * SIZE_OF_CHANGE,
                    rule=rule_selector,
                )
            ),
        )
