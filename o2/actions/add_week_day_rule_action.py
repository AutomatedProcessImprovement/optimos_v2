from dataclasses import replace
import random
from typing import Literal

import numpy as np

from o2.actions.base_actions.base_action import (
    BaseAction,
    BaseActionParamsType,
    RateSelfReturnType,
)
from o2.actions.batching_rule_action import (
    BatchingRuleAction,
    BatchingRuleActionParamsType,
)
from o2.models.days import DAY
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.state import State
from o2.models.timetable import rule_is_week_day
from o2.store import Store

SIZE_OF_CHANGE = 100
CLOSENESS_TO_MAX_WT = 0.01


class AddWeekDayRuleActionParamsType(BatchingRuleActionParamsType):
    """Parameter for AddWeekDayRuleAction."""

    add_days: list[DAY]


class AddWeekDayRuleAction(BatchingRuleAction, str=False):
    """AddWeekDayRuleAction will add a new day to the firing rules of a BatchingRule.

    It does this by cloning all the surrounding (AND) `FiringRule`s of
    the selected `FiringRule` and add one clone per `add_days` day to the BatchingRule.

    Why are we not also removing weekdays? This would result in simply removing the
    firing rule, which is already implemented in RemoveRuleAction.
    """

    params: AddWeekDayRuleActionParamsType

    def apply(self, state: State, enable_prints: bool = True) -> State:
        """Apply the action to the state."""
        timetable = state.timetable
        rule_selector = self.params["rule"]
        add_days = self.params["add_days"]

        index, rule = timetable.get_batching_rule(rule_selector)
        if rule is None or index is None:
            print(f"BatchingRule not found for {rule_selector}")
            return state

        firing_rule = rule.get_firing_rule(rule_selector)
        if not rule_is_week_day(firing_rule):
            print(f"Firing rule not found for {rule_selector}")
            return state

        if firing_rule.value in add_days:
            print("Day already present in the rule")
            return state

        assert rule_selector.firing_rule_index is not None
        or_index = rule_selector.firing_rule_index[0]
        and_rules = rule.firing_rules[or_index]

        and_index = rule_selector.firing_rule_index[1]

        new_or_rules = (
            rule.firing_rules[: or_index + 1]
            + [
                (
                    and_rules[:and_index]
                    + [replace(firing_rule, value=day)]
                    + and_rules[and_index + 1 :]
                )
                for day in add_days
            ]
            + rule.firing_rules[or_index + 1 :]
        )

        new_batching_rule = replace(
            rule,
            firing_rules=new_or_rules,
        )

        return state.replace_timetable(
            batch_processing=timetable.batch_processing[:index]
            + [new_batching_rule]
            + timetable.batch_processing[index + 1 :],
        )

    @staticmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        """Generate a best set of parameters & self-evaluates this action."""
        rule_selector = input.most_impactful_rule
        if rule_selector is None:
            return

        firing_rule = rule_selector.get_firing_rule_from_state(store.base_state)

        if not rule_is_week_day(firing_rule):
            return

        # TODO: Think of some smart heuristic to rate the action

        constraints = store.constraints.get_week_day_rule_constraints(
            rule_selector.batching_rule_task_id
        )

        if not constraints:
            return

        allowed_days = set(
            day
            for constraint in constraints
            for day in constraint.allowed_days
            if day != firing_rule.value
        )

        if len(allowed_days) == 0:
            return

        random_day = random.choice(list(allowed_days))

        yield (
            RATING.MEDIUM,
            AddWeekDayRuleAction(
                AddWeekDayRuleActionParamsType(
                    rule=rule_selector,
                    add_days=[random_day],
                )
            ),
        )
