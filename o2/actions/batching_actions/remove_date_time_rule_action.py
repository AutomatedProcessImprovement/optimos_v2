from dataclasses import replace

from typing_extensions import Required, override

from o2.actions.base_actions.base_action import BaseAction, BaseActionParamsType, RateSelfReturnType
from o2.models.days import DAY
from o2.models.self_rating import SelfRatingInput
from o2.models.state import State, TabuState
from o2.store import Store


class RemoveDateTimeRuleActionParamsType(BaseActionParamsType):
    """Parameter for RemoveDateTimeRuleAction."""

    task_id: Required[str]
    day: Required[DAY]


class RemoveDateTimeRuleAction(BaseAction):
    """RemoveDateTimeRuleAction will remove a day of week and time of day rule."""

    params: RemoveDateTimeRuleActionParamsType

    @override
    def apply(self, state: State, enable_prints: bool = True) -> State:
        timetable = state.timetable
        task_id = self.params["task_id"]

        best_selector = timetable.get_longest_time_period_for_daily_hour_firing_rules(
            task_id, self.params["day"]
        )

        if best_selector is None:
            return state

        day_selector, lower_bound_selector, upper_bound_selector = best_selector

        index, batching_rule = timetable.get_batching_rule(lower_bound_selector)
        assert batching_rule is not None and index is not None

        day_selector_index = (
            day_selector.firing_rule_index[1]
            if day_selector is not None and day_selector.firing_rule_index is not None
            else -1
        )
        lower_bound_index = (
            lower_bound_selector.firing_rule_index[1]
            if lower_bound_selector.firing_rule_index is not None
            else -1
        )
        upper_bound_index = (
            upper_bound_selector.firing_rule_index[1]
            if upper_bound_selector.firing_rule_index is not None
            else -1
        )
        assert upper_bound_selector.firing_rule_index is not None
        or_rules_index = upper_bound_selector.firing_rule_index[0]

        if or_rules_index >= len(batching_rule.firing_rules):
            return state

        new_and_rule = [
            and_rule
            for i, and_rule in enumerate(batching_rule.firing_rules[or_rules_index])
            if i
            not in [
                day_selector_index,
                lower_bound_index,
                upper_bound_index,
            ]
        ]
        new_batching_rule = replace(
            batching_rule,
            firing_rules=batching_rule.firing_rules[:or_rules_index]
            + ([new_and_rule] if new_and_rule else [])
            + batching_rule.firing_rules[or_rules_index + 1 :],
        )
        if len(new_batching_rule.firing_rules) == 0:
            return state.replace_timetable(
                batch_processing=timetable.batch_processing[:index] + timetable.batch_processing[index + 1 :],
            )

        return state.replace_timetable(
            batch_processing=timetable.batch_processing[:index]
            + [new_batching_rule]
            + timetable.batch_processing[index + 1 :],
        )

    @override
    @staticmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        raise NotImplementedError("Not implemented")
