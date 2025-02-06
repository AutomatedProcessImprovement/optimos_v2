from abc import ABC
from dataclasses import dataclass, replace

from typing_extensions import NotRequired

from o2.actions.base_actions.base_action import (
    BaseActionParamsType,
    RateSelfReturnType,
)
from o2.actions.base_actions.batching_rule_base_action import (
    BatchingRuleBaseAction,
)
from o2.models.days import DAY
from o2.models.self_rating import SelfRatingInput
from o2.models.state import State, TabuState
from o2.models.timetable import (
    BatchingRule,
    Distribution,
    rule_is_daily_hour,
)
from o2.store import Store


class ShiftDateTimeRuleBaseActionParamsType(BaseActionParamsType):
    """Parameter for ShiftDateTimeRuleBaseAction."""

    task_id: str
    day: DAY
    add_to_start: NotRequired[int]
    """How many hours to add to the start of the rule.
    (e.g. 1 = add 1 hour before, -1 = remove 1 hour after)"""
    add_to_end: NotRequired[int]
    """How many hours to add to the end of the rule.
    (e.g. 1 = add 1 hour after, -1 = remove 1 hour before)"""


@dataclass(frozen=True)
class ShiftDateTimeRuleBaseAction(BatchingRuleBaseAction, ABC, str=False):
    """ShiftDateTimeRuleBaseAction will shift a day of week and time of day rule."""

    params: ShiftDateTimeRuleBaseActionParamsType

    def apply(self, state: State, enable_prints: bool = True) -> State:
        """Create a copy of the timetable with the rule size modified."""
        timetable = state.timetable
        task_id = self.params["task_id"]
        add_to_start = self.params.get("add_to_start", 0)
        add_to_end = self.params.get("add_to_end", 0)

        best_selector = timetable.get_longest_time_period_for_daily_hour_firing_rules(
            task_id, self.params["day"]
        )

        if best_selector is None:
            # TODO: Here we should add a new rule
            return TabuState()

        # Modify Start / End
        _, lower_bound_selector, upper_bound_selector = best_selector
        batching_rule = lower_bound_selector.get_batching_rule_from_state(state)
        assert batching_rule is not None
        lower_bound_rule = lower_bound_selector.get_firing_rule_from_state(state)
        upper_bound_rule = upper_bound_selector.get_firing_rule_from_state(state)
        assert rule_is_daily_hour(lower_bound_rule)
        assert rule_is_daily_hour(upper_bound_rule)
        new_lower_bound = lower_bound_rule.value - add_to_start
        new_upper_bound = upper_bound_rule.value + add_to_end
        # TODO: Think about what happens < 0 or > 24
        new_lower_bound_rule = replace(lower_bound_rule, value=new_lower_bound)
        new_upper_bound_rule = replace(upper_bound_rule, value=new_upper_bound)
        new_batching_rule = batching_rule.replace_firing_rule(
            lower_bound_selector, new_lower_bound_rule, skip_merge=True
        ).replace_firing_rule(upper_bound_selector, new_upper_bound_rule)
        timetable = timetable.replace_batching_rule(
            lower_bound_selector, new_batching_rule
        )

        if enable_prints:
            print(
                f"\t\t>> Modifying rule {lower_bound_selector.id()} to new time bounds: {new_lower_bound} -> {new_upper_bound}"
            )

        return replace(state, timetable=timetable)

    def get_dominant_distribution(self, old_rule: BatchingRule) -> Distribution:
        """Find the size distribution with the highest probability."""
        return max(
            old_rule.size_distrib,
            key=lambda distribution: distribution.value,
        )


class ShiftDateTimeRuleAction(ShiftDateTimeRuleBaseAction):
    """ShiftDateTimeRuleAction will shift a day of week and time of day rule."""

    @staticmethod
    def rate_self(
        store: Store, input: SelfRatingInput
    ) -> RateSelfReturnType[ShiftDateTimeRuleBaseAction]:
        """Generate a best set of parameters & self-evaluates this action."""
        raise NotImplementedError("Not implemented")
