from dataclasses import replace
from datetime import datetime

from bpdfr_simulation_engine.execution_info import TaskEvent, Trace

from o2.actions.base_action import BaseAction, BaseActionParamsType, RateSelfReturnType
from o2.actions.batching_rule_action import (
    BatchingRuleAction,
    BatchingRuleActionParamsType,
)
from o2.models.constraints import RULE_TYPE
from o2.models.days import DAY
from o2.models.legacy_constraints import WorkMasks
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.state import State
from o2.models.timetable import (
    COMPARATOR,
    FiringRule,
    rule_is_daily_hour,
    rule_is_week_day,
)
from o2.store import Store

SIZE_OF_CHANGE = 1
CLOSENESS_TO_MAX_WT = 0.01


class ModifyDateTimeRulesByEnablementActionParamsType(BaseActionParamsType):
    """Parameter for ModifyDateTimeRulesByEnablementAction.

    hour_increment may also be negative to remove hours.
    """

    new_hour: int
    new_day: DAY
    task_id: str


class ModifyDateTimeRulesByEnablementAction(BaseAction):
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
        task_id = self.params["task_id"]
        new_hour = self.params["new_hour"]
        next_hour = new_hour + 1 if new_hour < 24 else 0
        new_day = self.params["new_day"]

        existing_task_rules = timetable.get_batching_rules_for_task(task_id)

        if not existing_task_rules:
            # TODO Also allow adding new rules
            return state

        # Find the rule to modify
        rule = existing_task_rules[0]
        index = timetable.batch_processing.index(rule)

        new_or_rule = [
            FiringRule(
                attribute=RULE_TYPE.WEEK_DAY,
                comparison=COMPARATOR.EQUAL,
                value=new_day,
            ),
            FiringRule(
                attribute=RULE_TYPE.DAILY_HOUR,
                comparison=COMPARATOR.GREATER_THEN_OR_EQUAL,
                value=new_hour,
            ),
            FiringRule(
                attribute=RULE_TYPE.DAILY_HOUR,
                comparison=COMPARATOR.LESS_THEN,
                value=next_hour,
            ),
        ]
        updated_rule = replace(
            rule,
            firing_rules=rule.firing_rules + [new_or_rule],
        )

        return state.replace_timetable(
            batch_processing=timetable.batch_processing[:index]
            + [updated_rule]
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
                                task_batch_enablement[rule.task_id] = (
                                    task_batch_enablement[
                                        rule.task_id
                                    ].set_hour_for_day(
                                        day_rule.value, firing_rule.value
                                    )
                                )

                            else:
                                task_batch_enablement[rule.task_id] = (
                                    task_batch_enablement[
                                        rule.task_id
                                    ].set_hour_for_every_day(firing_rule.value)
                                )

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
                                task_batch_enablement[rule.task_id] = (
                                    task_batch_enablement[
                                        rule.task_id
                                    ].set_hour_range_for_day(
                                        day_rule.value,
                                        less_than_rule.value,
                                        firing_rule.value,
                                    )
                                )
                            else:
                                task_batch_enablement[rule.task_id] = (
                                    task_batch_enablement[
                                        rule.task_id
                                    ].set_hour_range_for_every_day(
                                        less_than_rule.value,
                                        firing_rule.value,
                                    )
                                )

        # To the dict we also add all the times in the constraints
        for task_id in store.current_timetable.get_task_ids():
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

        # Now we iterate of over all enablement times in the event log, and add it to
        # a second dict (if it's not already in the first)
        enablement_counter: dict[tuple[str, DAY, int], int] = {}
        for trace in input.base_evaluation.cases:
            events: list[TaskEvent] = trace.event_list
            for event in events:
                enablement = event.enabled_datetime
                if not isinstance(enablement, datetime):
                    continue
                day: DAY = DAY[enablement.strftime("%A").upper()]
                hour = enablement.hour
                if task_batch_enablement[event.task_id].has_hour_for_day(day, hour):
                    continue

                if (event.task_id, day, hour) not in enablement_counter:
                    enablement_counter[(event.task_id, day, hour)] = 0
                enablement_counter[(event.task_id, day, hour)] += 1

        # Get task, day, hour with the most enablements
        most_enablement = max(
            enablement_counter.items(), key=lambda x: x[1], default=(None, None)
        )
        if most_enablement[0] is None:
            return

        task_id, day, hour = most_enablement[0]

        yield (
            RATING.HIGH,
            ModifyDateTimeRulesByEnablementAction(
                ModifyDateTimeRulesByEnablementActionParamsType(
                    task_id=task_id, new_day=day, new_hour=hour
                )
            ),
        )

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
