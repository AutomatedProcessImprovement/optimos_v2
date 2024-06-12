from dataclasses import replace
from o2.actions.base_action import BaseAction, BaseActionParamsType
from o2.types.state import State
from o2.types.timetable import COMPARATOR, BatchingRule, FiringRule, rule_is_week_day
from o2.types.constraints import RULE_TYPE
from o2.store import Store
from o2.types.self_rating import RATING, SelfRatingInput
from o2.types.days import DAY
import numpy as np

SIZE_OF_CHANGE = 100
CLOSENESS_TO_MAX_WT = 0.01


class AddWeekDayRuleActionParamsType(BaseActionParamsType):
    add_days: list[DAY]


class AddWeekDayRuleAction(BaseAction):
    params: AddWeekDayRuleActionParamsType

    # Returns a copy of the timetable with the rule size modified
    def apply(self, state: State, enable_prints=True):
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
                and_rules[:and_index]
                + [replace(firing_rule, value=day)]
                + and_rules[and_index + 1 :]
                for day in add_days
            ]
            + rule.firing_rules[or_index + 1 :]
        )

        new_batching_rule = replace(
            rule,
            firing_rules=new_or_rules,
        )

        return state.replaceTimetable(
            batch_processing=timetable.batch_processing[:index]
            + [new_batching_rule]
            + timetable.batch_processing[index + 1 :],
        )

    @staticmethod
    def rate_self(store: Store, input: SelfRatingInput):
        rule_selector = input.most_impactful_rule

        firing_rule = rule_selector.get_firing_rule_from_state(store.state)

        if not rule_is_week_day(firing_rule):
            return RATING.NOT_APPLICABLE, None

        # TODO: Think of some smart heuristic to rate the action

        constraints = store.constraints.get_week_day_rule_constraints(
            rule_selector.batching_rule_task_id
        )

        if not constraints:
            return RATING.NOT_APPLICABLE, None

        allowed_days = set(
            day
            for constraint in constraints
            for day in constraint.allowed_days
            if day != firing_rule.value
        )

        if len(allowed_days) == 0:
            return RATING.NOT_APPLICABLE, None

        random_day = np.random.choice(list(allowed_days))

        return (
            RATING.MEDIUM,
            AddWeekDayRuleAction(
                AddWeekDayRuleActionParamsType(
                    rule=rule_selector,
                    add_days=[random_day],
                )
            ),
        )
