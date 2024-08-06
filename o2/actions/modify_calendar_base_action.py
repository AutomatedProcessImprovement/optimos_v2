from abc import ABC, abstractmethod
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


class ModifyCalendarBaseActionParamsType(BaseActionParamsType):
    """Parameter for `ModifyCalendarBaseAction`."""

    calendar_id: str
    period_index: int
    day: DAY
    shift_hours: int
    add_hours_before: int


@dataclass(frozen=True)
class ModifyCalendarBaseAction(BaseAction, ABC):
    """`ModifyCalendarBaseAction` will modify the resource calendars.

    It's rating function will be implemented by it's subclasses.
    """

    params: ModifyCalendarBaseActionParamsType

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
    @abstractmethod
    def rate_self(
        store: Store, input: SelfRatingInput
    ) -> (
        tuple[Literal[RATING.NOT_APPLICABLE], None]
        | tuple[RATING, "ModifyCalendarBaseAction"]
    ):
        pass

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
