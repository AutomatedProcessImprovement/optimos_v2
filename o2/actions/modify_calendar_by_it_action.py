from dataclasses import dataclass, replace
from typing import Literal

from o2.actions.modify_calendar_base_action import (
    ModifyCalendarBaseAction,
    ModifyCalendarBaseActionParamsType,
)
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.timetable import ResourceCalendar
from o2.store import Store


class ModifyCalendarByITActionParamsType(ModifyCalendarBaseActionParamsType):
    """Parameter for `ModifyCalendarByITAction`."""


@dataclass(frozen=True)
class ModifyCalendarByITAction(ModifyCalendarBaseAction):
    """`ModifyCalendarByITAction` will modify the resource calendars based on wt.

    This action is based on the original optimos implementation,
    see `solution_traces_sorting_by_idle_times` in that project.

    It will first find the tasks with the most idle time, then find the days where
    those are executed the most, and then find the resources
    that does this task the most. (Although not for that day, as it was in Optimos).
    Then it will look at the resource calendars for those resources on those days,
    and first try to add hours to the end of the shifts, and if that is not possible,
    it will try to shift the shifts to start later. Finally it will try to add hours
    to be beginning & start of the shift.
    """

    @staticmethod
    def rate_self(
        store: Store, input: SelfRatingInput
    ) -> (
        tuple[Literal[RATING.NOT_APPLICABLE], None]
        | tuple[RATING, "ModifyCalendarByITAction"]
    ):
        """Generate a best set of parameters & self-evaluates this action."""
        base_evaluation = input.base_evaluation
        tasks = base_evaluation.get_task_names_sorted_by_idle_time_desc()
        for task in tasks:
            days = base_evaluation.get_most_frequent_enablement_weekdays(task)
            resources = base_evaluation.get_most_frequent_resources(task)
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
                        # We need to fix the day period to not change
                        # change the times of other days
                        fixed_day_period = replace(period, from_=day, to=day)

                        # Try to add hours to the end of the shift
                        new_period = fixed_day_period.add_hours_after(1)
                        if new_period is None:
                            continue
                        new_calendar = calendar.replace_time_period(index, new_period)
                        valid = ModifyCalendarByITAction._verify(store, new_calendar)
                        if valid:
                            return RATING.EXTREME, ModifyCalendarByITAction(
                                ModifyCalendarByITActionParamsType(
                                    calendar_id=calendar.id,
                                    period_index=index,
                                    day=day,
                                    add_hours_after=1,
                                )
                            )

                        # Try to shift the shift to begin later
                        new_period = fixed_day_period.shift_hours(-1)
                        if new_period is None:
                            continue
                        new_calendar = calendar.replace_time_period(index, new_period)
                        valid = ModifyCalendarByITAction._verify(store, new_calendar)
                        if valid:
                            return RATING.EXTREME, ModifyCalendarByITAction(
                                ModifyCalendarByITActionParamsType(
                                    calendar_id=calendar.id,
                                    period_index=index,
                                    day=day,
                                    shift_hours=-1,
                                )
                            )

                        # Try to add hours to the start & end of the shift
                        # TODO: Ask whether this shouldn't move up?
                        new_period = fixed_day_period.add_hours_before(1)
                        if new_period is None:
                            continue
                        new_period = new_period.add_hours_after(1)
                        if new_period is None:
                            continue
                        new_calendar = calendar.replace_time_period(index, new_period)
                        valid = ModifyCalendarByITAction._verify(store, new_calendar)
                        if valid:
                            return RATING.EXTREME, ModifyCalendarByITAction(
                                ModifyCalendarByITActionParamsType(
                                    calendar_id=calendar.id,
                                    period_index=index,
                                    day=day,
                                    add_hours_before=1,
                                    add_hours_after=1,
                                )
                            )

        return RATING.NOT_APPLICABLE, None