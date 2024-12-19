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
        batches_by_activity: dict[str, list[BatchInfo]] = {}
        for batch in store.current_evaluation.batches.values():
            activity = batch["activity"]
            if batch["idle_time"] == 0:
                continue
            if activity not in batches_by_activity:
                batches_by_activity[activity] = []
            batches_by_activity[activity].append(batch)

        for activity, batch_group in batches_by_activity.items():
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
                    first_enablement_weekday = DAY(
                        batch["accumulation_begin"].strftime("%A").upper()
                    )
                    required_processing_time = ceil(batch["ideal_proc"] / 3600)

                    time_periods = calendar.get_time_periods_of_length_excl_idle(
                        first_enablement_weekday,
                        required_processing_time,
                        start_time=batch["accumulation_begin"].hour,
                        last_start_time=batch["start"].hour + required_processing_time,
                    )

                    for period in time_periods:
                        required_large_wt = (
                            period.begin_time_hour - batch["accumulation_begin"].hour
                        )

                        yield (
                            AddDateTimeRuleBaseAction.get_default_rating(),
                            AddLargeWTRuleByIdleAction(
                                AddLargeWTRuleByIdleActionParamsType(
                                    task_id=activity,
                                    waiting_time=ceil(required_large_wt) * 3600,
                                    type=RULE_TYPE.LARGE_WT,
                                )
                            ),
                        )
