from collections import Counter

from o2.actions.base_actions.add_datetime_rule_base_action import (
    AddDateTimeRuleBaseAction,
    AddDateTimeRuleBaseActionParamsType,
)
from o2.actions.base_actions.base_action import (
    RateSelfReturnType,
)
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.time_period import TimePeriod
from o2.store import Store

# TODO: See if top 3 makes sense
LIMIT_OF_OPTIONS = 3


class AddDateTimeRuleByStartActionParamsType(AddDateTimeRuleBaseActionParamsType):
    """Parameter for AddDateTimeRuleByStartAction."""

    pass


class AddDateTimeRuleByStartAction(AddDateTimeRuleBaseAction):
    """AddDateTimeRuleByStartAction will add new daily_hour / weekday rules based on the start time of tasks.

    It does the following:
    1. Get all start times by resource (therefore we roughly know when a resource is available)
    2. Find the tasks with the most (batching) waiting time
    3. For that task get all assigned resources and their start times
    4. Find the most frequent intersection of those start times
    5. Add a new daily_hour / weekday rule for the task based on the start time
    """

    params: AddDateTimeRuleByStartActionParamsType

    @staticmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        """Generate a best set of parameters & self-evaluates this action."""
        evaluation = store.current_evaluation
        timetable = store.current_timetable

        start_times = evaluation.resource_started_weekdays

        sorted_tasks = sorted(
            store.current_evaluation.total_batching_waiting_time_per_task.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        for task_id, _ in sorted_tasks:
            resources_ids = timetable.get_resources_assigned_to_task(task_id)
            if not resources_ids:
                continue

            aggregated_start_times = {
                (day, hour): count
                for resource_id in resources_ids
                for day, times in start_times.get(resource_id, {}).items()
                for hour, count in times.items()
            }

            # find most frequent day,hour combination
            # Lets look at the top 3
            most_frequent_day_hour = Counter(aggregated_start_times).most_common(
                LIMIT_OF_OPTIONS
            )
            if not most_frequent_day_hour:
                continue

            for (day, hour), _ in most_frequent_day_hour:
                yield (
                    RATING.HIGH,
                    AddDateTimeRuleByStartAction(
                        AddDateTimeRuleByStartActionParamsType(
                            task_id=task_id,
                            time_period=TimePeriod.from_start_end(hour, hour + 1, day),
                            duration_fn=store.constraints.get_duration_fn_for_task(
                                task_id
                            ),
                        )
                    ),
                )
