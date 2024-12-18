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
from o2.models.self_rating import SelfRatingInput
from o2.models.timetable import RULE_TYPE
from o2.store import Store


class AddLargeWTRuleByIdleActionParamsType(AddReadyLargeWTRuleBaseActionParamsType):
    """Parameter for AddLargeWTRuleByIdleAction."""

    pass


class AddLargeWTRuleByIdleAction(AddReadyLargeWTRuleBaseAction):
    """An Action to add a LargeWT rule based on the idle time of the task.

    This action will add a new LargeWT rule based on the waiting time of the task.
    It does the following:
    1. Looks at all batches with idle time, grouped by their activity
    2. Calculate the average ideal_proc
    3. For each activity, look at all resources, which could also
       do that batch (incl. the one which originally did it)
    4. For each resource, find all time intervals/periods, that are are at
       least avg_ideal_proc long (only work-time, skipping idle time),
       and start after accumulation_begin. Up to a time after the actual
       batch start, that is at least avg_ideal_proc long.
    5. Get the shortest of these periods, remember the difference between the
       start of the period and the first enabled time of the batch.
    6. Average over all these differences for all resources.
    7. Create a new LargeWT rule for that average.
    """

    params: AddLargeWTRuleByIdleActionParamsType

    @staticmethod
    def rate_self(store: "Store", input: SelfRatingInput) -> RateSelfReturnType:
        """Generate a best set of parameters & self-evaluates this action."""

        evaluation = store.current_evaluation
        timetable = store.current_timetable
        state = store.current_state

        # Group all batches by activity
        batches_by_activity = {}
        for batch in store.current_evaluation.batches.values():
            activity = batch["activity"]
            if activity not in batches_by_activity:
                batches_by_activity[activity] = []
            batches_by_activity[activity].append(batch)

        for activity, batch_group in batches_by_activity.items():
            # Calculate the average ideal_proc
            ideal_proc = sum([batch["ideal_proc"] for batch in batch_group]) / len(
                batch_group
            )
            # For each activity, look at all resources, which could also
            # do that batch (incl. the one which originally did it)
            resources = timetable.get_resources_assigned_to_task(activity)
            for resource in resources:
                # For each resource, find all time intervals/periods, that are are at
                # least avg_ideal_proc long (only work-time, skipping idle time),
                # and start after accumulation_begin. Up to a time after the actual
                # batch start, that is at least avg_ideal_proc long.
                periods = []
                for batch in batch_group:
                    if batch["resource"] == resource:
                        # Find all time intervals/periods
                        # that are at least avg_ideal_proc long
                        # (only work-time, skipping idle time)
                        # and start after accumulation_begin
                        # Up to a time after the actual batch start,
                        # that is at least avg_ideal_proc long
                        pass
                # Get the shortest of these periods
                # remember the difference between the start of the period
                # and the first enabled time of the batch
                # Average over all these differences for all resources
                pass
            # Create a new LargeWT rule for that average
            pass
