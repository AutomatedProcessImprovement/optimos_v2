from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import Literal, Optional

from typing_extensions import NotRequired

from o2.actions.base_action import BaseAction, BaseActionParamsType
from o2.models.constraints import ConstraintsType
from o2.models.days import DAY
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.state import State
from o2.models.timetable import ResourceCalendar, TimePeriod, TimetableType
from o2.store import Store
from o2.util.indented_printer import print_l2


class ModifyResourceBaseActionParamsType(BaseActionParamsType):
    """Parameter for `ModifyResourceBaseAction`."""

    resource_id: str
    clone_resource: NotRequired[bool]
    remove_resource: NotRequired[bool]


@dataclass(frozen=True)
class ModifyResourceBaseAction(BaseAction, ABC):
    """`ModifyResourceBaseAction` will modify a resource or it's tasks.

    It's rating function will be implemented by it's subclasses.
    """

    params: ModifyResourceBaseActionParamsType

    def apply(self, state: State, enable_prints: bool = True) -> State:
        """Apply the action to the state."""
        if "remove_resource" in self.params and self.params["remove_resource"]:
            new_timetable = state.timetable.remove_resource(self.params["resource_id"])
            return replace(state, timetable=new_timetable)

    @staticmethod
    @abstractmethod
    def rate_self(
        store: Store, input: SelfRatingInput
    ) -> (
        tuple[Literal[RATING.NOT_APPLICABLE], None]
        | tuple[RATING, "ModifyResourceBaseAction"]
    ):
        """Rate the action based on the input.

        To be implemented by subclasses.
        """
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
            return f"{self.__class__.__name__}(Calender '{self.params['calendar_id']}' ({self.params['day']}) -- Shift {self.params['shift_hours']} hours)"  # noqa: E501
        elif "add_hours_after" in self.params:
            return f"{self.__class__.__name__}(Calender '{self.params['calendar_id']}' ({self.params['day']}) -- Add {self.params['add_hours_after']} hours after)"  # noqa: E501
        elif "add_hours_before" in self.params:
            return f"{self.__class__.__name__}(Calender '{self.params['calendar_id']}' ({self.params['day']}) -- Add {self.params['add_hours_before']} hours before)"  # noqa: E501
        elif "remove_period" in self.params:
            return f"{self.__class__.__name__}(Calender '{self.params['calendar_id']}' ({self.params['day']}) -- Remove)"  # noqa: E501
        return f"{self.__class__.__name__}(Calender '{self.params['calendar_id']}' ({self.params['day']}) -- Unknown)"  # noqa: E501
