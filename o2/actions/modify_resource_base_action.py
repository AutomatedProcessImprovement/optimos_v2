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
    task_id: NotRequired[str]
    clone_resource: NotRequired[bool]
    remove_resource: NotRequired[bool]
    remove_task_from_resource: NotRequired[bool]


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
        elif (
            "clone_resource" in self.params
            and self.params["clone_resource"]
            and "task_id" in self.params
        ):
            new_timetable = state.timetable.clone_resource(
                self.params["resource_id"],
                [self.params["task_id"]],
            )
            return replace(state, timetable=new_timetable)
        elif (
            "remove_task_from_resource" in self.params
            and self.params["remove_task_from_resource"]
            and "task_id" in self.params
        ):
            new_timetable = state.timetable.remove_task_from_resource(
                self.params["resource_id"],
                self.params["task_id"],
            )
            return replace(state, timetable=new_timetable)

    @staticmethod
    @abstractmethod
    def rate_self(
        store: Store, input: SelfRatingInput
    ) -> (
        tuple[Literal[RATING.NOT_APPLICABLE], None]
        | tuple[RATING, "ModifyResourceBaseAction"]
    ):
        """Generate a best set of parameters & self-evaluates this action.

        To be implemented by subclasses.
        """
        pass

    def __str__(self) -> str:
        """Return a string representation of the action."""
        if "remove_resource" in self.params and self.params["remove_resource"]:
            return f"{self.__class__.__name__}(Resource '{self.params['resource_id']}' -- Remove)"  # noqa: E501
        elif "clone_resource" in self.params and self.params["clone_resource"]:
            return f"{self.__class__.__name__}(Resource '{self.params['resource_id']}' -- Clone)"  # noqa: E501
        return f"{self.__class__.__name__}(Resource '{self.params['resource_id']}' -- Unknown)"
