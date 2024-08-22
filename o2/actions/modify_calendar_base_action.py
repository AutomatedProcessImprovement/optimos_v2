from abc import ABC, abstractmethod
from dataclasses import dataclass, replace

from typing_extensions import NotRequired

from o2.actions.base_action import BaseAction, BaseActionParamsType, RateSelfReturnType
from o2.models.days import DAY
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.state import State
from o2.models.timetable import ResourceCalendar, TimePeriod
from o2.store import Store
from o2.util.indented_printer import print_l2


class ModifyCalendarBaseActionParamsType(BaseActionParamsType):
    """Parameter for `ModifyCalendarBaseAction`."""

    calendar_id: str
    period_index: int
    day: DAY
    shift_hours: NotRequired[int]
    add_hours_before: NotRequired[int]
    add_hours_after: NotRequired[int]
    remove_period: NotRequired[bool]


@dataclass(frozen=True)
class ModifyCalendarBaseAction(BaseAction, ABC):
    """`ModifyCalendarBaseAction` will modify the resource calendars.

    It's rating function will be implemented by it's subclasses.
    """

    params: ModifyCalendarBaseActionParamsType

    def apply(self, state: State, enable_prints: bool = True) -> State:
        """Apply the action to the state."""
        calendar_id = self.params["calendar_id"]
        period_index = self.params["period_index"]
        day = self.params["day"]

        calendar = state.timetable.get_calendar(calendar_id)
        assert calendar is not None

        period = calendar.time_periods[period_index]
        fixed_day_period = replace(period, from_=period.from_, to=day)

        new_period = fixed_day_period
        if "shift_hours" in self.params:
            new_period = new_period.shift_hours(self.params["shift_hours"])
        if "add_hours_before" in self.params and new_period is not None:
            new_period = new_period.add_hours_before(self.params["add_hours_before"])
        if "add_hours_after" in self.params and new_period is not None:
            new_period = new_period.add_hours_after(self.params["add_hours_after"])
        if "remove_period" in self.params and self.params["remove_period"]:
            new_period = TimePeriod.empty()

        if new_period is None:
            return state

        if enable_prints:
            print_l2(f"Modification Made:{period} to {new_period}")

        new_calendar = calendar.replace_time_period(period_index, new_period)
        new_timetable = state.timetable.replace_resource_calendar(new_calendar)

        return replace(state, timetable=new_timetable)

    @staticmethod
    @abstractmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        pass

    @staticmethod
    def _verify(store: Store, new_calendar: ResourceCalendar) -> bool:
        if not new_calendar.is_valid():
            return False
        new_timetable = store.current_timetable.replace_resource_calendar(new_calendar)
        return store.constraints.verify_legacy_constraints(new_timetable)

    def __str__(self) -> str:
        """Return a string representation of the action."""
        if "shift_hours" in self.params:
            return f"{self.__class__.__name__}(Calender '{self.params['calendar_id']}' ({self.params['day']}-{self.params['period_index']}) -- Shift {self.params['shift_hours']} hours)"  # noqa: E501
        elif "add_hours_after" in self.params:
            return f"{self.__class__.__name__}(Calender '{self.params['calendar_id']}' ({self.params['day']}-{self.params['period_index']}) -- Add {self.params['add_hours_after']} hours after)"  # noqa: E501
        elif "add_hours_before" in self.params:
            return f"{self.__class__.__name__}(Calender '{self.params['calendar_id']}' ({self.params['day']}-{self.params['period_index']}) -- Add {self.params['add_hours_before']} hours before)"  # noqa: E501
        elif "remove_period" in self.params:
            return f"{self.__class__.__name__}(Calender '{self.params['calendar_id']}' ({self.params['day']}-{self.params['period_index']}) -- Remove)"  # noqa: E501
        return f"{self.__class__.__name__}(Calender '{self.params['calendar_id']}' ({self.params['day']}-{self.params['period_index']}) -- Unknown)"  # noqa: E501

    @staticmethod
    def get_default_rating(store: "Store") -> RATING:
        """Return the default rating for this action."""
        return RATING.HIGH if store.settings.optimize_calendar_first else RATING.LOW
