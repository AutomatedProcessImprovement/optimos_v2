from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal

from sympy import Symbol, lambdify

from o2.actions.base_action import BaseAction, BaseActionParamsType, RateSelfReturnType
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
)
from o2.store import Store

MARGIN_OF_ERROR = 0.03
SIZE_OF_CHANGE = 1


class ModifySizeRuleBaseActionParamsType(BatchingRuleActionParamsType):
    """Parameter for ModifySizeRuleBaseAction."""

    size_increment: int
    duration_fn: str


@dataclass(frozen=True)
class ModifySizeRuleBaseAction(BatchingRuleAction, ABC, str=False):
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
        pass

    @staticmethod
    def get_default_rating() -> RATING:
        """Return the default rating for this action."""
        return RATING.MEDIUM
