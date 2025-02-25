from datetime import datetime

from prosimos.execution_info import TaskEvent

from o2.actions.base_actions.add_datetime_rule_base_action import (
    AddDateTimeRuleBaseAction,
    AddDateTimeRuleBaseActionParamsType,
)
from o2.actions.base_actions.base_action import (
    RateSelfReturnType,
)
from o2.models.days import DAY
from o2.models.legacy_constraints import WorkMasks
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.time_period import TimePeriod
from o2.models.timetable import (
    COMPARATOR,
    rule_is_daily_hour,
    rule_is_week_day,
)
from o2.store import Store

SIZE_OF_CHANGE = 1
CLOSENESS_TO_MAX_WT = 0.01


class ModifyDateTimeRulesByEnablementActionParamsType(
    AddDateTimeRuleBaseActionParamsType
):
    """Parameter for ModifyDateTimeRulesByEnablementAction."""

    pass


class ModifyDateTimeRulesByEnablementAction(AddDateTimeRuleBaseAction):
    """ModifyDateTimeRulesByEnablementAction will modify DAILY_HOUR & WEEK_DAY rules.

    It's main metric is enablement. It looks at the enablement times of all rules, finds
    the rule with the most emblements outside of the current batching hours, and then tries
    to add it. If it can't (because of constraints) it will continue to the second most
    enablement, and so on.
    """

    params: ModifyDateTimeRulesByEnablementActionParamsType

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
                        if firing_rule.is_eq:
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

                        elif firing_rule.is_gt:
                            less_than_rule = next(
                                (
                                    less_than_rule
                                    for less_than_rule in and_rules
                                    if rule_is_daily_hour(less_than_rule)
                                    and less_than_rule.is_lt
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
                        for allowed_hour in constraint.allowed_hours[day]:
                            task_batch_enablement[task_id] = task_batch_enablement[
                                task_id
                            ].set_hour_for_day(day, allowed_hour)

        # Now we iterate of over all enablement times in the event log, and add it to
        # a second dict (if it's not already in the first)
        enablement_counter: dict[tuple[str, DAY, int], int] = {}
        # TODO: Fix this
        for trace in input.parent_evaluation.cases:
            events: list[TaskEvent] = trace.event_list
            for event in events:
                enablement = event.enabled_datetime
                if not isinstance(enablement, datetime):
                    continue
                day: DAY = DAY.from_date(enablement)
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
            RATING.MEDIUM,
            ModifyDateTimeRulesByEnablementAction(
                ModifyDateTimeRulesByEnablementActionParamsType(
                    task_id=task_id,
                    time_period=TimePeriod.from_start_end(hour, hour + 1, day),
                )
            ),
        )

        return
