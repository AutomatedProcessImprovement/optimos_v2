from math import ceil

from o2.actions.base_actions.add_datetime_rule_base_action import (
    AddDateTimeRuleBaseAction,
    AddDateTimeRuleBaseActionParamsType,
)
from o2.actions.base_actions.add_ready_large_wt_rule_base_action import (
    AddReadyLargeWTRuleBaseAction,
    AddReadyLargeWTRuleBaseActionParamsType,
)
from o2.actions.base_actions.base_action import (
    RateSelfReturnType,
)
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.timetable import RULE_TYPE
from o2.store import Store


class AddLargeWTRuleByWTActionParamsType(AddReadyLargeWTRuleBaseActionParamsType):
    """Parameter for AddLargeWTRuleByWTAction."""

    pass


class AddLargeWTRuleByWTAction(AddReadyLargeWTRuleBaseAction):
    """An Action to add a LargeWT rule based on the waiting time of the task.

    This action will add a new LargeWT rule based on the waiting time of the task.
    It does the following:
    1. Find the task with the highest (batching) waiting time.
    2. Create a new LargeWT rule for 90% of the waiting time.
    """

    params: AddLargeWTRuleByWTActionParamsType

    @staticmethod
    def rate_self(
        store: "Store", input: SelfRatingInput
    ) -> RateSelfReturnType["AddLargeWTRuleByWTAction"]:
        """Generate a best set of parameters & self-evaluates this action."""
        sorted_tasks = sorted(
            store.current_evaluation.total_batching_waiting_time_per_task.items(),
            key=lambda x: x[1],
            reverse=True,
        )
        for task_id, _ in sorted_tasks:
            waiting_time = store.current_evaluation.avg_batching_waiting_time_per_task[
                task_id
            ]
            if waiting_time == 0:
                continue
            # Cap the waiting time to 24 hours
            new_large_wt = min(ceil(waiting_time * 0.9), 24 * 60 * 60)
            yield (
                RATING.VERY_LOW,
                AddLargeWTRuleByWTAction(
                    AddLargeWTRuleByWTActionParamsType(
                        task_id=task_id,
                        waiting_time=new_large_wt,
                        type=RULE_TYPE.LARGE_WT,
                    )
                ),
            )
