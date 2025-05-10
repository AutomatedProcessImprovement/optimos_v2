from dataclasses import replace
from typing import Literal

from typing_extensions import override

from o2.actions.base_actions.base_action import RateSelfReturnType
from o2.actions.base_actions.batching_rule_base_action import (
    BatchingRuleBaseAction,
    BatchingRuleBaseActionParamsType,
)
from o2.models.evaluation import Evaluation
from o2.models.rule_selector import RuleSelector
from o2.models.self_rating import RATING
from o2.models.state import State
from o2.models.timetable import rule_is_daily_hour
from o2.store import Store
from o2.util.helper import select_variant, select_variants
from o2.util.logger import warn

SIZE_OF_CHANGE = 1
CLOSENESS_TO_MAX_WT = 0.01


class ModifyDailyHourRuleActionParamsType(BatchingRuleBaseActionParamsType):
    """Parameter for ModifyDailyHourRuleAction.

    hour_increment may also be negative to remove hours.
    """

    hour_increment: int


class ModifyDailyHourRuleAction(BatchingRuleBaseAction, str=False):
    """ModifyDailyHourRuleAction will add a new day to the firing rules of a BatchingRule.

    It does this by cloning all the surrounding (AND) `FiringRule`s of
    the selected `FiringRule` and add one clone per `add_days` day to the BatchingRule.

    Why are we not also removing weekdays? This would result in simply removing the
    firing rule, which is already implemented in RemoveRuleAction.
    """

    params: ModifyDailyHourRuleActionParamsType

    @override
    def apply(self, state: State, enable_prints: bool = True) -> State:
        timetable = state.timetable
        rule_selector = self.params["rule"]
        hour_increment = self.params["hour_increment"]

        index, rule = timetable.get_batching_rule(rule_selector)
        if rule is None or index is None:
            warn(f"BatchingRule not found for {rule_selector}")
            return state

        firing_rule = rule.get_firing_rule(rule_selector)
        if not rule_is_daily_hour(firing_rule):
            warn(f"Firing rule not found for {rule_selector}")
            return state

        if hour_increment == 0:
            warn(f"No change in hours for {str(self)}")
            return state

        new_hour = int(firing_rule.value) + hour_increment
        if (new_hour < 0) or (new_hour > 24):
            warn(f"Hour out of bounds ({new_hour}) for {str(self)}")
            return state

        assert rule_selector.firing_rule_index is not None

        new_batching_rule = rule.replace_firing_rule(rule_selector, replace(firing_rule, value=new_hour))

        return state.replace_timetable(
            batch_processing=timetable.batch_processing[:index]
            + [new_batching_rule]
            + timetable.batch_processing[index + 1 :],
        )

    @override
    @staticmethod
    def rate_self(store: Store, input: Evaluation) -> RateSelfReturnType:
        selectors = [
            RuleSelector(
                batching_rule_task_id=batching_rule.task_id,
                firing_rule_index=(or_rule_index, and_rule_index),
            )
            for batching_rule in store.current_timetable.batch_processing
            for or_rule_index, or_rules in enumerate(batching_rule.firing_rules)
            for and_rule_index, rule in enumerate(or_rules)
            if rule_is_daily_hour(rule) and not rule.is_eq
        ]
        for selector in select_variants(store, selectors):
            for hour_increment in select_variants(store, [1, -1], inner=True):
                yield (
                    RATING.LOW,
                    ModifyDailyHourRuleAction(
                        ModifyDailyHourRuleActionParamsType(rule=selector, hour_increment=hour_increment),
                    ),
                )

        return
