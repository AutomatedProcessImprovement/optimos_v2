from dataclasses import dataclass, replace
from typing import Literal, Optional

from o2.actions.base_action import BaseAction, BaseActionParamsType
from o2.models.constraints import ConstraintsType
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.state import State
from o2.models.timetable import ResourceCalendar, TimetableType
from o2.store import Store


class ModifyCalendarByWTActionParamsType(BaseActionParamsType):
    """Parameter for `ModifyCalendarByWTAction`."""

    updated_calendar: ResourceCalendar


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
        return replace(
            state,
            timetable=state.timetable.replace_resource_calendar(
                self.params["updated_calendar"]
            ),
        )

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
                    periods = calendar.get_periods_for_day(day)
                    for index, period in enumerate(periods):
                        # Try to add hours to the start of the shift
                        new_period = period.add_hours_before(1)
                        new_calendar = calendar.replace_time_period(index, new_period)
                        action = ModifyCalendarByWTAction._verify_and_build_action(
                            store, new_calendar
                        )
                        if action is not None:
                            return RATING.EXTREME, action

                        # Try to shift the shift to start earlier
                        new_period = period.shift_hours(-1)
                        new_calendar = calendar.replace_time_period(index, new_period)
                        action = ModifyCalendarByWTAction._verify_and_build_action(
                            store, new_calendar
                        )
                        if action is not None:
                            return RATING.EXTREME, action

        return RATING.NOT_APPLICABLE, None

    @staticmethod
    def _verify_and_build_action(
        store: Store,
        new_calendar: ResourceCalendar,
    ) -> Optional["ModifyCalendarByWTAction"]:
        if not new_calendar.is_valid():
            return None
        new_timetable = store.current_timetable.replace_resource_calendar(new_calendar)
        if not store.constraints.verify_legacy_constraints(new_timetable):
            return None
        return ModifyCalendarByWTAction(params={"updated_calendar": new_calendar})
