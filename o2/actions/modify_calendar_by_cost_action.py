from dataclasses import dataclass, replace
from typing import Literal

from o2.actions.base_action import (
    RateSelfReturnType,
)
from o2.actions.modify_calendar_base_action import (
    ModifyCalendarBaseAction,
    ModifyCalendarBaseActionParamsType,
)
from o2.models.days import DAYS
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.time_period import TimePeriod
from o2.store import Store


class ModifyCalendarByCostActionParamsType(ModifyCalendarBaseActionParamsType):
    """Parameter for `ModifyCalendarByCostAction`."""


@dataclass(frozen=True)
class ModifyCalendarByCostAction(ModifyCalendarBaseAction):
    """`ModifyCalendarByCostAction` will modify the resource calendars based on wt.

    This action is based on the original optimos implementation,
    see `solution_traces_optimize_cost` in that project.

    It will fist iterate over all resources sorted by their
    cost (cost/hour * available_time), for each resource it will iterate over
    each day in their calendar. For each day it will try to modify the
    first period (shift), by either removing it (if it's only 1 hour long),
    shrinking it from start & end, shrinking it from the start,
    or finally shrinking it from the end.
    """

    @staticmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        """Generate a best set of parameters & self-evaluates this action."""
        resources = store.state.timetable.get_resources_with_cost()
        for resource, _cost in resources:
            calendar = store.current_timetable.get_calendar(resource.calendar)
            if calendar is None:
                continue

            for day in DAYS:
                periods = calendar.get_periods_containing_day(day)
                for period in periods:
                    index = calendar.time_periods.index(period)
                    # We need to fix the day period to not change
                    # change the times of other days
                    fixed_day_period = period.model_copy(
                        update={"from_": day, "to": day}
                    )

                    # Try to remove the period if it's only 1 hour long
                    if fixed_day_period.duration == 1:
                        new_calendar = calendar.replace_time_period(
                            index, TimePeriod.empty()
                        )
                        valid = ModifyCalendarByCostAction._verify(store, new_calendar)
                        if valid:
                            yield (
                                ModifyCalendarByCostAction.get_default_rating(store),
                                ModifyCalendarByCostAction(
                                    params=ModifyCalendarByCostActionParamsType(
                                        calendar_id=calendar.id,
                                        period_index=index,
                                        day=day,
                                        remove_period=True,
                                    )
                                ),
                            )
                    # Try to shrink the period from start & end
                    new_period = fixed_day_period.add_hours_after(-1)
                    if new_period is not None:
                        new_period = new_period.add_hours_before(-1)
                        if new_period is not None:
                            new_calendar = calendar.replace_time_period(
                                index, new_period
                            )
                            valid = ModifyCalendarByCostAction._verify(
                                store, new_calendar
                            )
                            if valid:
                                yield (
                                    ModifyCalendarByCostAction.get_default_rating(
                                        store
                                    ),
                                    ModifyCalendarByCostAction(
                                        params=ModifyCalendarByCostActionParamsType(
                                            calendar_id=calendar.id,
                                            period_index=index,
                                            day=day,
                                            add_hours_before=-1,
                                            add_hours_after=-1,
                                        )
                                    ),
                                )
                    # Try to shrink the period from start
                    new_period = fixed_day_period.add_hours_before(-1)
                    if new_period is not None:
                        new_calendar = calendar.replace_time_period(index, new_period)
                        valid = ModifyCalendarByCostAction._verify(store, new_calendar)
                        if valid:
                            yield (
                                ModifyCalendarByCostAction.get_default_rating(store),
                                ModifyCalendarByCostAction(
                                    params=ModifyCalendarByCostActionParamsType(
                                        calendar_id=calendar.id,
                                        period_index=index,
                                        day=day,
                                        add_hours_before=-1,
                                    )
                                ),
                            )
                    # Try to shrink the period from end
                    new_period = fixed_day_period.add_hours_after(-1)
                    if new_period is not None:
                        new_calendar = calendar.replace_time_period(index, new_period)
                        valid = ModifyCalendarByCostAction._verify(store, new_calendar)
                        if valid:
                            yield (
                                ModifyCalendarByCostAction.get_default_rating(store),
                                ModifyCalendarByCostAction(
                                    params=ModifyCalendarByCostActionParamsType(
                                        calendar_id=calendar.id,
                                        period_index=index,
                                        day=day,
                                        add_hours_after=-1,
                                    )
                                ),
                            )

        return
