import random

from typing_extensions import override

from o2.actions.base_actions.add_datetime_rule_base_action import (
    AddDateTimeRuleAction,
    AddDateTimeRuleBaseActionParamsType,
)
from o2.actions.base_actions.add_ready_large_wt_rule_base_action import (
    AddReadyLargeWTRuleAction,
    AddReadyLargeWTRuleBaseActionParamsType,
)
from o2.actions.base_actions.add_size_rule_base_action import (
    AddSizeRuleAction,
    AddSizeRuleBaseActionParamsType,
)
from o2.actions.base_actions.base_action import (
    BaseAction,
    BaseActionParamsType,
    RateSelfReturnType,
)
from o2.actions.base_actions.batching_rule_base_action import BatchingRuleBaseAction
from o2.actions.base_actions.modify_size_rule_base_action import (
    ModifySizeRuleAction,
    ModifySizeRuleBaseActionParamsType,
)
from o2.actions.batching_actions.modify_daily_hour_rule_action import (
    ModifyDailyHourRuleAction,
    ModifyDailyHourRuleActionParamsType,
)
from o2.actions.batching_actions.remove_rule_action import (
    RemoveRuleAction,
    RemoveRuleActionParamsType,
)
from o2.models.days import DAYS
from o2.models.evaluation import Evaluation
from o2.models.self_rating import RATING
from o2.models.settings import Settings
from o2.models.solution import Solution
from o2.models.timetable import RULE_TYPE
from o2.models.timetable.time_period import TimePeriod
from o2.store import Store

ACTIONS: list[type[BaseAction]] = [
    AddDateTimeRuleAction,
    AddReadyLargeWTRuleAction,
    AddSizeRuleAction,
    ModifyDailyHourRuleAction,
    ModifySizeRuleAction,
    RemoveRuleAction,
]


class RandomActionParamsType(BaseActionParamsType):
    """Parameter for RandomAction."""

    pass


class RandomAction(BaseAction):
    """RandomAction will randomly select an action and apply it to the timetable.

    This is only used by the Random Agents.
    """

    params: RandomActionParamsType

    @override
    @staticmethod
    def rate_self(store: Store, input: Solution) -> RateSelfReturnType:
        timetable = input.timetable
        params: BaseActionParamsType | None = None

        # We generate infinite actions
        while True:
            # Randomly select an action
            action = random.choice(ACTIONS)

            if action == AddDateTimeRuleAction:
                task_id = random.choice(timetable.get_task_ids())
                random_day = random.choice(DAYS)
                random_start_time = random.randint(0, 23)
                end_time = random_start_time + 1
                time_period = TimePeriod.from_start_end(random_start_time, end_time, random_day)
                duration_fn = store.constraints.get_duration_fn_for_task(task_id)

                params = AddDateTimeRuleBaseActionParamsType(
                    task_id=task_id,
                    time_period=time_period,
                    duration_fn=duration_fn,
                )
            elif action == AddReadyLargeWTRuleAction:
                task_id = random.choice(timetable.get_task_ids())
                waiting_time = random.randint(1, 24 * 60 * 60)
                rule_type = random.choice([RULE_TYPE.LARGE_WT, RULE_TYPE.READY_WT])
                duration_fn = store.constraints.get_duration_fn_for_task(task_id)
                params = AddReadyLargeWTRuleBaseActionParamsType(
                    task_id=task_id,
                    waiting_time=waiting_time,
                    type=rule_type,  # type: ignore
                    duration_fn=duration_fn,
                )
            elif action == AddSizeRuleAction:
                task_id = random.choice(timetable.get_task_ids())
                size = 2
                duration_fn = store.constraints.get_duration_fn_for_task(task_id)
                params = AddSizeRuleBaseActionParamsType(
                    task_id=task_id,
                    size=size,
                    duration_fn=duration_fn,
                )
            elif action == ModifyDailyHourRuleAction:
                all_daily_hour_rule_selectors = [
                    rule_selector
                    for batching_rule in timetable.batch_processing
                    for rule_selector in batching_rule.get_firing_rule_selectors(RULE_TYPE.DAILY_HOUR)
                ]
                if not all_daily_hour_rule_selectors:
                    continue
                hour_increment = random.choice([-1, 1])
                random_rule_selector = random.choice(all_daily_hour_rule_selectors)
                params = ModifyDailyHourRuleActionParamsType(
                    rule=random_rule_selector,
                    hour_increment=hour_increment,
                    duration_fn=store.constraints.get_duration_fn_for_task(
                        random_rule_selector.batching_rule_task_id
                    ),
                )
            elif action == ModifySizeRuleAction:
                all_size_rule_selectors = [
                    rule_selector
                    for batching_rule in timetable.batch_processing
                    for rule_selector in batching_rule.get_firing_rule_selectors(RULE_TYPE.SIZE)
                ]
                if not all_size_rule_selectors:
                    continue
                random_rule_selector = random.choice(all_size_rule_selectors)
                task_id = random.choice(timetable.get_task_ids())
                size_increment = random.choice([-1, 1])
                duration_fn = store.constraints.get_duration_fn_for_task(task_id)
                params = ModifySizeRuleBaseActionParamsType(
                    rule=random_rule_selector,
                    size_increment=size_increment,
                    duration_fn=duration_fn,
                )
            elif action == RemoveRuleAction:
                if Settings.DISABLE_REMOVE_ACTION_RULE:
                    continue
                all_rule_selectors = [
                    rule_selector
                    for batching_rule in timetable.batch_processing
                    for rule_selector in batching_rule.get_firing_rule_selectors()
                ]
                if not all_rule_selectors:
                    continue
                random_rule_selector = random.choice(all_rule_selectors)
                params = RemoveRuleActionParamsType(rule=random_rule_selector)
            else:
                raise ValueError(f"Unknown action: {action}")

            yield (RATING.HIGH, action(params))
