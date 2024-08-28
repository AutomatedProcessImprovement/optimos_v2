from dataclasses import replace

from o2.actions.base_action import RateSelfReturnType
from o2.actions.batching_rule_action import (
    BatchingRuleAction,
    BatchingRuleActionParamsType,
)
from o2.models.days import DAY
from o2.models.legacy_constraints import WorkMasks
from o2.models.self_rating import SelfRatingInput
from o2.models.state import State
from o2.models.timetable import COMPARATOR, rule_is_daily_hour, rule_is_week_day
from o2.store import Store

SIZE_OF_CHANGE = 1
CLOSENESS_TO_MAX_WT = 0.01


class ModifyDateTimeRulesByEnablementActionParamsType(BatchingRuleActionParamsType):
    """Parameter for ModifyDateTimeRulesByEnablementAction.

    hour_increment may also be negative to remove hours.
    """

    new_hour: int
    new_day: DAY


class ModifyDateTimeRulesByEnablementAction(BatchingRuleAction):
    """ModifyDateTimeRulesByEnablementAction will modify DAILY_HOUR & WEEK_DAY rules.

    It's main metric is enablement. It looks at the enablement times of all rules, finds
    the rule with the most emblements outside of the current batching hours, and then tries
    to add it. If it can't (because of constraints) it will continue to the second most
    enablement, and so on.
    """

    params: ModifyDateTimeRulesByEnablementActionParamsType

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

        # We first create a dict of all tasks and their respective enablement times (if any)
        # This is modeled as a WorkMasks (aka bitmask for each day)
        # This dict basically marks the times not interesting for us, because they are
        # already enabled.
        task_batch_enablement: dict[str, WorkMasks] = {}
        for rule in store.current_timetable.batch_processing:
            for and_rules in rule.firing_rules:
                for firing_rule in and_rules:
                    if rule_is_daily_hour(firing_rule):
                        if rule.task_id not in task_batch_enablement:
                            task_batch_enablement[rule.task_id] = WorkMasks()
                        day_rule = next(
                            (
                                day_rule
                                for day_rule in and_rules
                                if rule_is_week_day(day_rule)
                            ),
                            None,
                        )
                        has_day = day_rule is not None
                        if firing_rule.comparison == COMPARATOR.EQUAL:
                            if has_day:
                                task_batch_enablement[
                                    rule.task_id
                                ] = task_batch_enablement[
                                    rule.task_id
                                ].set_hour_for_day(day_rule.value, firing_rule.value)

                            else:
                                task_batch_enablement[
                                    rule.task_id
                                ] = task_batch_enablement[
                                    rule.task_id
                                ].set_hour_for_every_day(firing_rule.value)

                        elif firing_rule.comparison == COMPARATOR.GREATER_THEN:
                            less_than_rule = next(
                                (
                                    less_than_rule
                                    for less_than_rule in and_rules
                                    if rule_is_daily_hour(less_than_rule)
                                    and less_than_rule.comparison
                                    == COMPARATOR.LESS_THEN
                                ),
                                None,
                            )
                            assert less_than_rule is not None
                            if has_day:
                                task_batch_enablement[
                                    rule.task_id
                                ] = task_batch_enablement[
                                    rule.task_id
                                ].set_hour_range_for_day(
                                    day_rule.value,
                                    less_than_rule.value,
                                    firing_rule.value,
                                )
                            else:
                                task_batch_enablement[
                                    rule.task_id
                                ] = task_batch_enablement[
                                    rule.task_id
                                ].set_hour_range_for_every_day(
                                    less_than_rule.value,
                                    firing_rule.value,
                                )

        # To the dict we also add all the times in the constraints
        for distribution in store.current_timetable.task_resource_distribution:
            task_id = distribution.task_id
            constraints = store.constraints.get_daily_hour_rule_constraints(task_id)
            if task_id not in task_batch_enablement:
                task_batch_enablement[task_id] = WorkMasks()
            if constraints is None:
                task_batch_enablement[task_id] = WorkMasks().all_day()
            else:
                for constraint in constraints:
                    day_constraints = store.constraints.get_week_day_rule_constraints(
                        task_id
                    )
                    allowed_days = set(
                        day
                        for day_constraint in day_constraints
                        for day in day_constraint.allowed_days
                    )
                    for day in allowed_days:
                        for allowed_hour in constraint.allowed_hours:
                            task_batch_enablement[task_id] = task_batch_enablement[
                                task_id
                            ].set_hour_for_day(day, allowed_hour)

        # for rule_selector in possible_candidates:
        #     if rule_selector is None:
        #         continue

        #     rule = rule_selector.get_firing_rule_from_state(store.state)
        #     if rule is None:
        #         continue

        #     if not rule_is_daily_hour(rule):
        #         continue

        #     if rule.comparison == COMPARATOR.EQUAL:
        #         # TODO Do something with EQUAL
        #         continue

        #     constraints = store.constraints.get_daily_hour_rule_constraints(
        #         rule_selector.batching_rule_task_id
        #     )
        #     if constraints is None:
        #         continue

        #     hour_change = 0
        #     if rule_selector == most_increase_selector and "<" in rule.comparison:
        #         hour_change = SIZE_OF_CHANGE * 1
        #     elif rule_selector == most_increase_selector and ">" in rule.comparison:
        #         hour_change = SIZE_OF_CHANGE * -1
        #     elif rule_selector == most_reduction_selector and ">" in rule.comparison:
        #         hour_change = SIZE_OF_CHANGE * 1
        #     elif rule_selector == most_reduction_selector and "<" in rule.comparison:
        #         hour_change = SIZE_OF_CHANGE * -1

        #     else:
        #         continue

        #     new_hour = rule.value + hour_change
        #     if new_hour < 0 or new_hour > 24:
        #         continue

        #     allowed_hours = set(
        #         hour for constraint in constraints for hour in constraint.allowed_hours
        #     )
        #     if new_hour not in allowed_hours:
        #         continue
        #     yield (
        #         RATING.MEDIUM,
        #         ModifyDateTimeRulesByEnablementAction(
        #             ModifyDateTimeRulesByEnablementActionParamsType(
        #                 rule=rule_selector, hour_increment=hour_change
        #             )
        #         ),
        #     )

        return
