from abc import ABC, abstractmethod
from dataclasses import dataclass, replace

from sympy import Symbol, lambdify
from typing_extensions import override

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
    BatchingRule,
    Distribution,
    rule_is_size,
)
from o2.store import Store
from o2.util.logger import warn


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

    @override
    def apply(self, state: State, enable_prints: bool = True) -> State:
        timetable = state.timetable
        rule_selector = self.params["rule"]

        _, batching_rule = timetable.get_batching_rule(rule_selector)
        if batching_rule is None:
            warn(f"BatchingRule not found for {rule_selector}")
            return state

        firing_rule = batching_rule.get_firing_rule(rule_selector)
        if firing_rule is None:
            warn(f"FiringRule not found for {rule_selector}")
            return state

        if not rule_is_size(firing_rule):
            return state

        new_size = int(firing_rule.value) + self.params["size_increment"]
        # We don't allow size 1, as that basically means no batching
        if new_size <= 1:
            return state

        new_firing_rule = replace(firing_rule, value=new_size)

        new_timetable = state.timetable.replace_firing_rule(rule_selector, new_firing_rule)

        return replace(state, timetable=new_timetable)

    def get_dominant_distribution(self, old_rule: BatchingRule) -> Distribution:
        """Find the size distribution with the highest probability."""
        return max(
            old_rule.size_distrib,
            key=lambda distribution: distribution.value,
        )

    @override
    @staticmethod
    @abstractmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        pass

    @staticmethod
    def get_default_rating() -> RATING:
        """Return the default rating for this action."""
        return RATING.MEDIUM


class ModifySizeRuleAction(ModifySizeRuleBaseAction):
    """ModifySizeRuleAction will modify the size of a BatchingRule."""

    @override
    @staticmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        raise NotImplementedError("Not implemented")
