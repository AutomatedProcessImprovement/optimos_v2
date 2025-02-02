from abc import ABC, abstractmethod
from dataclasses import dataclass

from sympy import Symbol, lambdify

from o2.actions.base_actions.base_action import (
    RateSelfReturnType,
)
from o2.actions.base_actions.batching_rule_base_action import (
    BatchingRuleBaseAction,
    BatchingRuleBaseActionParamsType,
)
from o2.models.constraints import RULE_TYPE
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.state import State, TabuState
from o2.models.timetable import (
    COMPARATOR,
    BatchingRule,
    Distribution,
    FiringRule,
)
from o2.store import Store

MARGIN_OF_ERROR = 0.03
SIZE_OF_CHANGE = 1


class ModifySizeRuleBaseActionParamsType(BatchingRuleBaseActionParamsType):
    """Parameter for ModifySizeRuleBaseAction."""

    size_increment: int
    duration_fn: str


@dataclass(frozen=True)
class ModifySizeRuleBaseAction(BatchingRuleBaseAction, ABC, str=False):
    """ModifySizeRuleBaseAction will modify the size of a BatchingRule.

    This will effect the size distribution and the duration distribution of the rule,
    as well as the firing rule.
    """

    params: ModifySizeRuleBaseActionParamsType

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

        if new_size < 1:
            return TabuState()

        new_rule = BatchingRule.from_task_id(
            task_id=old_rule.task_id,
            size=new_size,
            firing_rules=[
                # TODO: Do not replace the whole firing rules,
                # just the one that needs to be changed
                FiringRule(
                    attribute=RULE_TYPE.SIZE,
                    comparison=COMPARATOR.GREATER_THEN_OR_EQUAL,
                    value=new_size,
                )
            ],
        )

        if enable_prints:
            print(
                f"\t\t>> Modifying rule {old_rule.id()} to new size = {old_size} -> {new_size} & duration_modifier = {fn(new_size)}"  # noqa: E501
            )

        return state.replace_timetable(
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
    @abstractmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        """Generate a best set of parameters & self-evaluates this action."""
        pass

    @staticmethod
    def get_default_rating() -> RATING:
        """Return the default rating for this action."""
        return RATING.MEDIUM


class ModifySizeRuleAction(ModifySizeRuleBaseAction):
    """ModifySizeRuleAction will modify the size of a BatchingRule."""

    @staticmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        """Generate a best set of parameters & self-evaluates this action."""
        raise NotImplementedError("Not implemented")
