from math import ceil

from o2.actions.base_actions.add_datetime_rule_base_action import (
    AddDateTimeRuleBaseAction,
    AddDateTimeRuleBaseActionParamsType,
)
from o2.actions.base_actions.base_action import (
    RateSelfReturnType,
)
from o2.models.self_rating import RATING
from o2.models.solution import Solution
from o2.store import Store


class AddDateTimeRuleByAvailabilityActionParamsType(AddDateTimeRuleBaseActionParamsType):
    """Parameter for AddDateTimeRuleByAvailabilityAction."""

    pass


class AddDateTimeRuleByAvailabilityAction(AddDateTimeRuleBaseAction):
    """An Action to add daily_hour / weekday batching rules based on availability.

    This action will add a new daily_hour / weekday rule based on the availability of the task.
    It does the following:
    1. Find the task with the highest processing time.
    2. Get the average processing time for the task.
    3. Find the most frequent availability time period for the task, with min. hours needed.
    4. Add a new daily_hour / weekday rule for the task based on the availability.
    """

    params: AddDateTimeRuleByAvailabilityActionParamsType

    @staticmethod
    def rate_self(
        store: "Store", input: "Solution"
    ) -> RateSelfReturnType["AddDateTimeRuleByAvailabilityAction"]:
        """Generate a best set of parameters & self-evaluates this action."""
        timetable = input.state.timetable

        avg_processing_times = input.evaluation.get_average_processing_time_per_task()

        sorted_tasks = sorted(
            store.current_evaluation.get_total_duration_time_per_task().items(),
            key=lambda x: x[1],
            reverse=True,
        )
        for task_id, _ in sorted_tasks:
            avg_processing_time = avg_processing_times[task_id]
            hours_needed = ceil(avg_processing_time / 60 / 60)
            best_time_period = timetable.get_highest_availability_time_period(task_id, hours_needed)
            if best_time_period is None:
                continue

            yield (
                RATING.HIGH,
                AddDateTimeRuleByAvailabilityAction(
                    AddDateTimeRuleByAvailabilityActionParamsType(
                        task_id=task_id,
                        time_period=best_time_period,
                        duration_fn=store.constraints.get_duration_fn_for_task(task_id),
                    )
                ),
            )
        return
