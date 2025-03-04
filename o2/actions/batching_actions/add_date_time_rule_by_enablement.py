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

LIMIT_OF_OPTIONS = 5


class AddDateTimeRuleByEnablementActionParamsType(AddDateTimeRuleBaseActionParamsType):
    """Parameter for AddDateTimeRuleByEnablementAction."""

    pass


class AddDateTimeRuleByEnablementAction(AddDateTimeRuleBaseAction):
    """AddDateTimeRuleByEnablementAction will add new daily_hour / weekday rules based on the enablement of the task.

    It does the following:
    1. gets the tasks with the most waiting time
    2. finds the most frequent enablement datetime for the task
    3. add a new daily_hour / weekday rule for the task based on the enablement datetime
       to the most frequent task-datetime pair.
    """

    params: AddDateTimeRuleByEnablementActionParamsType

    @staticmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        """Generate a best set of parameters & self-evaluates this action."""
        evaluation = store.current_evaluation
        task_enablement_weekdays = evaluation.task_enablement_weekdays

        sorted_tasks = sorted(
            store.current_evaluation.total_batching_waiting_time_per_task.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        task_enablements = {
            task_id: sorted(
                (
                    (count, day, hour)
                    for day, hours in dict.items()
                    for hour, count in hours.items()
                ),
                key=lambda x: x[0],
                reverse=True,
            )
            for task_id, dict in task_enablement_weekdays.items()
        }

        for task_id, waiting_time in sorted_tasks:
            # If we got no waiting time, we can stop
            if waiting_time < 1:
                break
            task_enablement_pairs = task_enablements[task_id][:LIMIT_OF_OPTIONS]
            for _, day, hour in task_enablement_pairs:
                yield (
                    RATING.HIGH,
                    AddDateTimeRuleByEnablementAction(
                        AddDateTimeRuleByEnablementActionParamsType(
                            task_id=task_id,
                            time_period=TimePeriod.from_start_end(hour, hour + 1, day),
                            duration_fn=store.constraints.get_duration_fn_for_task(
                                task_id
                            ),
                        )
                    ),
                )

        return
