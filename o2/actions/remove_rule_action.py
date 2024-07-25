from dataclasses import dataclass
from typing import Literal

from o2.actions.base_action import BaseAction, BaseActionParamsType
from o2.actions.batching_rule_action import (
    BatchingRuleAction,
    BatchingRuleActionParamsType,
)
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.state import State
from o2.store import Store


class RemoveRuleActionParamsType(BatchingRuleActionParamsType):
    """Parameter for `RemoveRuleAction`."""

    pass


@dataclass(frozen=True)
class RemoveRuleAction(BatchingRuleAction):
    """`RemoveRuleAction` will remove a `FiringRule` from a `BatchingRule`."""

    params: RemoveRuleActionParamsType

    def apply(self, state: State, enable_prints: bool = True) -> State:
        """Create a copy of the timetable with the rule removed."""
        timetable = state.timetable
        rule_selector = self.params["rule"]

        index, rule = timetable.get_batching_rule(rule_selector)
        if rule is None or index is None:
            print(f"BatchingRule not found for {rule_selector}")
            return state
        if enable_prints:
            print(f"\t\t>> Removing rule {rule_selector}")

        new_batching_rule = rule.remove_firing_rule(rule_selector)
        if new_batching_rule is None:
            return state.replaceTimetable(
                batch_processing=timetable.batch_processing[:index]
                + timetable.batch_processing[index + 1 :],
            )

        return state.replaceTimetable(
            batch_processing=timetable.batch_processing[:index]
            + [new_batching_rule]
            + timetable.batch_processing[index + 1 :],
        )

    @staticmethod
    def rate_self(
        store: Store, input: SelfRatingInput
    ) -> (
        tuple[Literal[RATING.NOT_APPLICABLE], None] | tuple[RATING, "RemoveRuleAction"]
    ):
        """Create a set of parameters & rate this action."""
        rule_selector = input.most_wt_increase
        if rule_selector is None:
            return RATING.NOT_APPLICABLE, None

        evaluation = input.most_wt_increase_evaluation

        constraints = store.constraints.get_batching_size_rule_constraints(
            rule_selector.batching_rule_task_id
        )

        max_allowed_min_size = max(
            [constraint.min_size for constraint in constraints], default=1
        )
        if max_allowed_min_size > 0:
            return RATING.NOT_APPLICABLE, None

        # TODO: Check constraints
        # Check if this evaluation beats the current pareto front
        if store.current_pareto_front.is_dominated_by(evaluation):
            print(
                f"\t\t>> Most impactful rule dominates current. Rule: {rule_selector}"
            )
            return (
                RATING.LOW,
                RemoveRuleAction(RemoveRuleActionParamsType(rule=rule_selector)),
            )
        return RATING.NOT_APPLICABLE, None
