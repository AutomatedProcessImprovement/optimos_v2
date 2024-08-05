from dataclasses import dataclass, replace
from typing import Literal, Optional

from o2.actions.base_action import BaseAction, BaseActionParamsType
from o2.models.constraints import ConstraintsType
from o2.models.days import DAY
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.state import State
from o2.models.timetable import ResourceCalendar, TimetableType
from o2.store import Store
from o2.util.indented_printer import print_l2


class ModifyCalendarByWTActionParamsType(BaseActionParamsType):
    """Parameter for `ModifyCalendarByWTAction`."""

    calendar_id: str
    period_index: int
    day: DAY
    shift_hours: int
    add_hours_before: int


@dataclass(frozen=True)
class ModifyCalendarByWTAction(BaseAction):
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

    params: ModifyCalendarByWTActionParamsType

    def apply(self, state: State, enable_prints: bool = True) -> State:
        """Create a copy of the timetable with the rule removed."""
        calendar_id = self.params["calendar_id"]
        period_index = self.params["period_index"]
        day = self.params["day"]

        calendar = state.timetable.get_calendar(calendar_id)
        assert calendar is not None

        period = calendar.time_periods[period_index]
        fixed_day_period = replace(period, from_=period.from_, to=day)
        if self.params["shift_hours"] != 0:
            new_period = fixed_day_period.shift_hours(self.params["shift_hours"])
        elif self.params["add_hours_before"] != 0:
            new_period = fixed_day_period.add_hours_before(
                self.params["add_hours_before"]
            )
        else:
            return state

        if new_period is None:
            return state

        if enable_prints:
            print_l2(f"Modification Made:{period} to {new_period}")

        new_calendar = calendar.replace_time_period(period_index, new_period)
        new_timetable = state.timetable.replace_resource_calendar(new_calendar)

        return replace(state, timetable=new_timetable)

    @staticmethod
    def rate_self(
        store: Store, input: SelfRatingInput
    ) -> (
        tuple[Literal[RATING.NOT_APPLICABLE], None]
        | tuple[RATING, "ModifyCalendarByWTAction"]
    ):
        base_evaluation = input.base_evaluation
        tasks = base_evaluation.get_task_names_sorted_by_waiting_time_desc()
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

                        # Try to add hours to the start of the shift
                        new_period = fixed_day_period.add_hours_before(1)
                        if new_period is None:
                            continue
                        new_calendar = calendar.replace_time_period(index, new_period)
                        valid = ModifyCalendarByWTAction._verify(store, new_calendar)
                        if valid:
                            return RATING.EXTREME, ModifyCalendarByWTAction(
                                ModifyCalendarByWTActionParamsType(
                                    calendar_id=calendar.id,
                                    period_index=index,
                                    day=day,
                                    add_hours_before=1,
                                    shift_hours=0,
                                )
                            )

                        # Try to shift the shift to start earlier
                        new_period = fixed_day_period.shift_hours(-1)
                        if new_period is None:
                            continue
                        new_calendar = calendar.replace_time_period(index, new_period)
                        valid = ModifyCalendarByWTAction._verify(store, new_calendar)
                        if valid:
                            return RATING.EXTREME, ModifyCalendarByWTAction(
                                ModifyCalendarByWTActionParamsType(
                                    calendar_id=calendar.id,
                                    period_index=index,
                                    day=day,
                                    add_hours_before=0,
                                    shift_hours=1,
                                )
                            )

        return RATING.NOT_APPLICABLE, None

    @staticmethod
    def _verify(store: Store, new_calendar: ResourceCalendar) -> bool:
        if not new_calendar.is_valid():
            return False
        new_timetable = store.current_timetable.replace_resource_calendar(new_calendar)
        return store.constraints.verify_legacy_constraints(new_timetable)

    def __str__(self) -> str:
        """Return a string representation of the action."""
        if self.params["shift_hours"] > 0:
            return f"{self.__class__.__name__}(Calender '{self.params['calendar_id']}' ({self.params['day']}) -- Shift {self.params['shift_hours']} hours)"  # noqa: E501
        return f"{self.__class__.__name__}(Calender '{self.params['calendar_id']}' ({self.params['day']}) -- Add {self.params['add_hours_before']} hours before)"  # noqa: E501
