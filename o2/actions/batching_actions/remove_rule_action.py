import random
from dataclasses import dataclass

from o2.actions.base_actions.base_action import (
    RateSelfReturnType,
)
from o2.actions.base_actions.batching_rule_base_action import (
    BatchingRuleBaseAction,
    BatchingRuleBaseActionParamsType,
)
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.settings import Settings
from o2.models.state import State
from o2.store import Store
from o2.util.logger import warn


class RemoveRuleActionParamsType(BatchingRuleBaseActionParamsType):
    """Parameter for `RemoveRuleAction`."""

    pass


@dataclass(frozen=True)
class RemoveRuleAction(BatchingRuleBaseAction, str=False):
    """`RemoveRuleAction` will remove a `FiringRule` from a `BatchingRule`.

    It will not be smart about this, but just yield random firing rules to remove
    """

    params: RemoveRuleActionParamsType

    def apply(self, state: State, enable_prints: bool = True) -> State:
        """Create a copy of the timetable with the rule removed."""
        timetable = state.timetable
        rule_selector = self.params["rule"]

        index, rule = timetable.get_batching_rule(rule_selector)
        if rule is None or index is None:
            warn(f"BatchingRule not found for {rule_selector}")
            return state
        if enable_prints:
            warn(f"\t\t>> Removing rule {rule_selector}")

        new_batching_rule = rule.remove_firing_rule(rule_selector)
        if new_batching_rule is None:
            return state.replace_timetable(
                batch_processing=timetable.batch_processing[:index]
                + timetable.batch_processing[index + 1 :],
            )

        return state.replace_timetable(
            batch_processing=timetable.batch_processing[:index]
            + [new_batching_rule]
            + timetable.batch_processing[index + 1 :],
        )

    @staticmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        """Create a set of parameters & rate this action."""
        if Settings.DISABLE_REMOVE_ACTION_RULE:
            return (
                RATING.NOT_APPLICABLE,
                None,
            )

        selectors = [
            rule_selector
            for batching_rule in store.current_timetable.batch_processing
            for rule_selector in batching_rule.get_firing_rule_selectors()
        ]

        random.shuffle(selectors)
        for rule_selector in selectors:
            yield (
                RATING.VERY_LOW,
                RemoveRuleAction(RemoveRuleActionParamsType(rule=rule_selector)),
            )
