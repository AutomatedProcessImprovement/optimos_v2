import random
from math import ceil

from o2.actions.base_actions.add_datetime_rule_base_action import (
    AddDateTimeRuleBaseAction,
)
from o2.actions.base_actions.add_ready_large_wt_rule_base_action import (
    AddReadyLargeWTRuleBaseAction,
    AddReadyLargeWTRuleBaseActionParamsType,
)
from o2.actions.base_actions.base_action import (
    RateSelfReturnType,
)
from o2.models.days import DAY
from o2.models.self_rating import SelfRatingInput
from o2.models.timetable import RULE_TYPE
from o2.store import Store
from o2.util.waiting_time_helper import BatchInfo

# TODO: See if top 5 makes sense
LIMIT_OF_OPTIONS = 5


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
    7. Create a new LargeWT rule for every of those periods

    TODO: Use average and do not create for every single one
    """

    params: AddLargeWTRuleByIdleActionParamsType

    @staticmethod
    def rate_self(
        store: "Store", input: SelfRatingInput
    ) -> RateSelfReturnType["AddLargeWTRuleByIdleAction"]:
        """Generate a best set of parameters & self-evaluates this action."""
        timetable = store.current_timetable

        # Group all batches by activity, only include those with idle time
        batches_by_activity = store.current_evaluation.batches_by_activity_with_idle

        # Sort the activities by the highest idle time
        sorted_activities = sorted(
            batches_by_activity.keys(),
            key=lambda x: sum(batch["idle_time"] for batch in batches_by_activity[x]),
            reverse=True,
        )

        for activity in sorted_activities:
            batch_group = batches_by_activity[activity]
            # For each activity, look at all resources, which could also
            # do that batch (incl. the one which originally did it)

            resources = timetable.get_resources_assigned_to_task(activity)
            for resource in resources:
                # For each resource, find all time intervals/periods, that are are at
                # least avg_ideal_proc long (only work-time, skipping idle time),
                # and start after accumulation_begin. Up to a time after the actual
                # batch start, that is at least avg_ideal_proc long.
                calendar = timetable.get_calendar_for_resource(resource)
                if calendar is None:
                    continue
                for batch in batch_group:
                    first_enablement_weekday = DAY.from_date(
                        batch["accumulation_begin"]
                    )
                    required_processing_time = ceil(batch["ideal_proc"] / 3600)

                    time_periods = calendar.get_time_periods_of_length_excl_idle(
                        first_enablement_weekday,
                        required_processing_time,
                        start_time=batch["accumulation_begin"].hour,
                        last_start_time=batch["start"].hour + required_processing_time,
                    )

                    proposed_waiting_times = set()

                    for period in time_periods:
                        required_large_wt = (
                            period.begin_time_hour - batch["accumulation_begin"].hour
                        )
                        # Idle time of 0 doesn't make sense,
                        # as it's basically the same as no batching
                        if required_large_wt <= 0:
                            continue

                        waiting_time = ceil(required_large_wt) * 3600
                        # If we already proposed this waiting time, skip
                        if waiting_time in proposed_waiting_times:
                            continue
                        proposed_waiting_times.add(waiting_time)

                        yield (
                            AddLargeWTRuleByIdleAction.get_default_rating(),
                            AddLargeWTRuleByIdleAction(
                                AddLargeWTRuleByIdleActionParamsType(
                                    task_id=activity,
                                    waiting_time=waiting_time,
                                    type=RULE_TYPE.LARGE_WT,
                                )
                            ),
                        )
