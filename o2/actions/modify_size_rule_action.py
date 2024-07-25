from dataclasses import dataclass
from typing import Literal

from sympy import Symbol, lambdify

from o2.actions.base_action import BaseAction, BaseActionParamsType
from o2.actions.batching_rule_action import (
    BatchingRuleAction,
    BatchingRuleActionParamsType,
)
from o2.models.constraints import RULE_TYPE
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.state import State
from o2.models.timetable import (
    COMPARATOR,
    BatchingRule,
    Distribution,
    FiringRule,
    rule_is_size,
)
from o2.store import Store

MARGIN_OF_ERROR = 0.03
SIZE_OF_CHANGE = 1


class ModifySizeRuleActionParamsType(BatchingRuleActionParamsType):
    """Parameter for ModifySizeRuleAction."""

    size_increment: int
    duration_fn: str


@dataclass(frozen=True)
class ModifySizeRuleAction(BatchingRuleAction):
    """ModifySizeRuleAction will modify the size of a BatchingRule.

    This will effect the size distribution and the duration distribution of the rule,
    as well as the firing rule.
    """

    params: ModifySizeRuleActionParamsType

    def apply(self, state: State, enable_prints: bool = True) -> State:
        """Create a copy of the timetable with the rule size modified."""
        timetable = state.timetable
        rule_selector = self.params["rule"]

        (rule_index, old_rule) = timetable.get_batching_rule(rule_selector)
        if old_rule is None or rule_index is None:
            print(f"BatchingRule not found for {rule_selector}")
            return state
        old_size = self.get_dominant_distribution(old_rule).key
        new_size = int(old_size) + self.params["size_increment"]
        fn = lambdify(Symbol("size"), self.params["duration_fn"])

        size_distrib = [
            Distribution(
                key=str(new_size),
                value=1,
            ),
        ]
        if new_size != 1:
            size_distrib.insert(
                0,
                Distribution(
                    key=str(1),
                    value=0,
                ),
            )

        duration_distrib = [
            Distribution(
                key=str(new_size),
                value=fn(new_size),
            )
        ]

        # TODO: Do not replace the whole firing rules,
        # just the one that needs to be changed
        firing_rules = [
            [
                FiringRule(
                    attribute=RULE_TYPE.SIZE,
                    comparison=COMPARATOR.EQUAL,
                    value=new_size,
                )
            ]
        ]
        new_rule = BatchingRule(
            task_id=old_rule.task_id,
            type=old_rule.type,
            size_distrib=size_distrib,
            duration_distrib=duration_distrib,
            firing_rules=firing_rules,
        )

        if enable_prints:
            print(
                f"\t\t>> Modifying rule {old_rule.id()} to new size = {old_size} -> {new_size} & duration_modifier = {fn(new_size)}"  # noqa: E501
            )

        return state.replaceTimetable(
            batch_processing=timetable.batch_processing[:rule_index]
            + [new_rule]
            + timetable.batch_processing[rule_index + 1 :],
        )

    def get_dominant_distribution(self, old_rule: BatchingRule) -> Distribution:
        """Find the size distribution with the highest probability."""
        return max(
            old_rule.size_distrib,
            key=lambda distribution: distribution.value,
        )

    @staticmethod
    def rate_self(
        store: Store, input: SelfRatingInput
    ) -> (
        tuple[Literal[RATING.NOT_APPLICABLE], None]
        | tuple[RATING, "ModifySizeRuleAction"]
    ):
        """Create a "optimal" action & it's rating."""
        rule_selector = input.most_impactful_rule
        evaluation = input.most_impactful_rule_evaluation

        firing_rule = rule_selector.get_firing_rule_from_state(store.state)

        if not rule_is_size(firing_rule):
            return RATING.NOT_APPLICABLE, None

        # TODO Get current fastest evaluation by task
        base_evaluation = store.current_fastest_evaluation

        base_avg_waiting_time = base_evaluation.get_avg_waiting_time_of_task_id(
            rule_selector.batching_rule_task_id, store
        )
        new_avg_waiting_time = evaluation.get_avg_waiting_time_of_task_id(
            rule_selector.batching_rule_task_id, store
        )

        # This rule does reduce the waiting time, not increment it
        if new_avg_waiting_time > base_avg_waiting_time:
            size_increment = SIZE_OF_CHANGE
            # If the change is only very small, we don't want to apply it
            if 1 - (base_avg_waiting_time / new_avg_waiting_time) < MARGIN_OF_ERROR:
                return RATING.NOT_APPLICABLE, None
        else:
            size_increment = -1 * SIZE_OF_CHANGE
            # If the change is only very small, we don't want to apply it
            if 1 - (new_avg_waiting_time / base_avg_waiting_time) < MARGIN_OF_ERROR:
                return RATING.NOT_APPLICABLE, None

        new_size = firing_rule.value + size_increment

        if new_size < 1:
            # We don't want to go below 1, here the remove rule action should be used
            return RATING.NOT_APPLICABLE, None

        constraints = store.constraints.get_batching_size_rule_constraints(
            rule_selector.batching_rule_task_id
        )

        max_allowed_min_size = max(
            [constraint.min_size for constraint in constraints], default=1
        )
        min_allowed_max_size = min(
            [constraint.max_size for constraint in constraints], default=1
        )

        # Decrementing the size would break the constraints
        if new_size < max_allowed_min_size or new_size > min_allowed_max_size:
            return RATING.NOT_APPLICABLE, None

        return (
            RATING.MEDIUM,
            ModifySizeRuleAction(
                ModifySizeRuleActionParamsType(
                    size_increment=size_increment,
                    # TODO: Don't arbitrarily choose duration fn [0]
                    duration_fn=constraints[0].duration_fn,
                    rule=rule_selector,
                )
            ),
        )
