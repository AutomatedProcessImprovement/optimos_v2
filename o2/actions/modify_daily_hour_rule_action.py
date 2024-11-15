from dataclasses import replace
from typing import Literal

from o2.actions.base_action import RateSelfReturnType
from o2.actions.batching_rule_action import (
    BatchingRuleAction,
    BatchingRuleActionParamsType,
)
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.state import State
from o2.models.timetable import COMPARATOR, rule_is_daily_hour
from o2.store import Store

SIZE_OF_CHANGE = 1
CLOSENESS_TO_MAX_WT = 0.01


class ModifyDailyHourRuleActionParamsType(BatchingRuleActionParamsType):
    """Parameter for ModifyDailyHourRuleAction.

    hour_increment may also be negative to remove hours.
    """

    hour_increment: int


class ModifyDailyHourRuleAction(BatchingRuleAction, str=False):
    """ModifyDailyHourRuleAction will add a new day to the firing rules of a BatchingRule.

    It does this by cloning all the surrounding (AND) `FiringRule`s of
    the selected `FiringRule` and add one clone per `add_days` day to the BatchingRule.

    Why are we not also removing weekdays? This would result in simply removing the
    firing rule, which is already implemented in RemoveRuleAction.
    """

    params: ModifyDailyHourRuleActionParamsType

    def apply(self, state: State, enable_prints: bool = True) -> State:
        """Apply the action to the state."""
        timetable = state.timetable
        rule_selector = self.params["rule"]
        hour_increment = self.params["hour_increment"]

        index, rule = timetable.get_batching_rule(rule_selector)
        if rule is None or index is None:
            print(f"BatchingRule not found for {rule_selector}")
            return state

        firing_rule = rule.get_firing_rule(rule_selector)
        if not rule_is_daily_hour(firing_rule):
            print(f"Firing rule not found for {rule_selector}")
            return state

        if hour_increment == 0:
            print("No change in hours")
            return state

        new_hour = firing_rule.value + hour_increment
        if (new_hour < 0) or (new_hour > 24):
            print("Hour out of bounds")
            return state

        assert rule_selector.firing_rule_index is not None

        new_batching_rule = rule.replace_firing_rule(
            rule_selector, replace(firing_rule, value=new_hour)
        )

        return state.replace_timetable(
            batch_processing=timetable.batch_processing[:index]
            + [new_batching_rule]
            + timetable.batch_processing[index + 1 :],
        )

    @staticmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        """Generate a best set of parameters & self-evaluates this action."""
        most_reduction_selector = input.most_wt_reduction
        most_increase_selector = input.most_wt_increase

        # TODO Clean this loop up, and think of a better style, e.g. moving it
        # to a helper fn

        possible_candidates = (
            [
                most_reduction_selector,
                most_increase_selector,
            ]
            if most_reduction_selector == input.most_impactful_rule
            else [
                most_increase_selector,
                most_reduction_selector,
            ]
        )

        for rule_selector in possible_candidates:
            if rule_selector is None:
                continue

            rule = rule_selector.get_firing_rule_from_state(store.base_state)
            if rule is None:
                continue

            if not rule_is_daily_hour(rule):
                continue

            if rule.comparison == COMPARATOR.EQUAL:
                # TODO Do something with EQUAL
                continue

            constraints = store.constraints.get_daily_hour_rule_constraints(
                rule_selector.batching_rule_task_id
            )
            if constraints is None:
                continue

            hour_change = 0
            if rule_selector == most_increase_selector and "<" in rule.comparison:
                hour_change = SIZE_OF_CHANGE * 1
            elif rule_selector == most_increase_selector and ">" in rule.comparison:
                hour_change = SIZE_OF_CHANGE * -1
            elif rule_selector == most_reduction_selector and ">" in rule.comparison:
                hour_change = SIZE_OF_CHANGE * 1
            elif rule_selector == most_reduction_selector and "<" in rule.comparison:
                hour_change = SIZE_OF_CHANGE * -1

            else:
                continue

            new_hour = rule.value + hour_change
            if new_hour < 0 or new_hour > 24:
                continue

            allowed_hours = set(
                hour for constraint in constraints for hour in constraint.allowed_hours
            )
            if new_hour not in allowed_hours:
                # TODO: We need to get the relevant day constraint here, or if none
                # is applicable, we'll need to check if any day constraint forbids
                # this hour
                continue
            yield (
                RATING.MEDIUM,
                ModifyDailyHourRuleAction(
                    ModifyDailyHourRuleActionParamsType(
                        rule=rule_selector, hour_increment=hour_change
                    )
                ),
            )

        return
