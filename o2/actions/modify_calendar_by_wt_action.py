from dataclasses import dataclass, replace
from typing import Literal

from o2.actions.base_action import RateSelfReturnType
from o2.actions.modify_calendar_base_action import (
    ModifyCalendarBaseAction,
    ModifyCalendarBaseActionParamsType,
)
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.timetable import ResourceCalendar
from o2.store import Store


class ModifyCalendarByWTActionParamsType(ModifyCalendarBaseActionParamsType):
    """Parameter for `ModifyCalendarByWTAction`."""


@dataclass(frozen=True)
class ModifyCalendarByWTAction(ModifyCalendarBaseAction, str=False):
    """`ModifyCalendarByWTAction` will modify the resource calendars based on wt.

    This action is based on the original optimos implementation,
    see `solution_traces_sorting_by_waiting_times` in that project.

    It will first find the tasks with the most waiting time, then find the days where
    those are executed the most, and then find the resources
    that does this task the most. (Although not for that day, as it was in Optimos).
    Then it will look at the resource calendars for those resources on those days,
    and first try to add hours to the start of the shifts, and if that is not possible,
    it will try to shift the shifts to start earlier.
    """

    @staticmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        """Generate a best set of parameters & self-evaluates this action."""
        parent_evaluation = input.parent_evaluation
        tasks = parent_evaluation.get_task_names_sorted_by_waiting_time_desc()
        for task in tasks:
            days = parent_evaluation.get_most_frequent_enablement_weekdays(task)
            resources = parent_evaluation.get_most_frequent_resources(task)
            for day in days:
                for resource in resources:
                    calendar = store.current_timetable.get_calendar_for_resource(
                        resource
                    )
                    if calendar is None:
                        continue
                    periods = calendar.get_periods_containing_day(day)
                    for period in periods:
                        index = calendar.time_periods.index(period)
                        period_id = period.id
                        # We need to fix the day period to not change
                        # change the times of other days
                        fixed_day_period = period.model_copy(
                            update={"from_": day, "to": day}
                        )

                        # Try to add hours to the start of the shift
                        new_period = fixed_day_period.add_hours_before(1)
                        if new_period is None:
                            continue
                        new_calendar = calendar.replace_time_period(index, new_period)
                        valid = ModifyCalendarByWTAction._verify(store, new_calendar)
                        if valid:
                            yield (
                                ModifyCalendarByWTAction.get_default_rating(store),
                                ModifyCalendarByWTAction(
                                    ModifyCalendarByWTActionParamsType(
                                        calendar_id=calendar.id,
                                        period_id=period_id,
                                        day=day,
                                        add_hours_before=1,
                                    )
                                ),
                            )

                        # Try to shift the shift to start earlier
                        new_period = fixed_day_period.shift_hours(-1)
                        if new_period is None:
                            continue
                        new_calendar = calendar.replace_time_period(index, new_period)
                        valid = ModifyCalendarByWTAction._verify(store, new_calendar)
                        if valid:
                            yield (
                                ModifyCalendarByWTAction.get_default_rating(store),
                                ModifyCalendarByWTAction(
                                    ModifyCalendarByWTActionParamsType(
                                        calendar_id=calendar.id,
                                        period_id=period_id,
                                        day=day,
                                        add_hours_before=0,
                                        shift_hours=-1,
                                    )
                                ),
                            )

        return
