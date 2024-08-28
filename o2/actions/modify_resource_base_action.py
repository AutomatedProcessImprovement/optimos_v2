from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from typing_extensions import NotRequired

from o2.actions.base_action import BaseAction, BaseActionParamsType, RateSelfReturnType
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.state import State

if TYPE_CHECKING:
    from o2.store import Store


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
        return state

    @staticmethod
    @abstractmethod
    def rate_self(store: "Store", input: SelfRatingInput) -> RateSelfReturnType:
        """Generate a best set of parameters & self-evaluates this action.

        To be implemented by subclasses.
        """
        pass

    def __str__(self) -> str:
        """Return a string representation of the action."""
        if "remove_resource" in self.params:
            return f"{self.__class__.__name__}(Resource '{self.params['resource_id']}' -- Remove)"  # noqa: E501
        elif "clone_resource" in self.params:
            return f"{self.__class__.__name__}(Resource '{self.params['resource_id']}' -- Clone)"  # noqa: E501
        elif "remove_task_from_resource" in self.params and "task_id" in self.params:
            return f"{self.__class__.__name__}(Resource '{self.params['resource_id']}' -- Remove Task '{self.params['task_id']}')"  # noqa: E501
        return f"{self.__class__.__name__}(Resource '{self.params['resource_id']}' -- Unknown)"

    @staticmethod
    def get_default_rating(store: "Store") -> RATING:
        """Get the default rating for this action."""
        if store.settings.legacy_combined_mode_status.enabled:
            return (
                RATING.HIGH
                if store.settings.legacy_combined_mode_status.resource_is_next
                else RATING.LOW
            )
        return RATING.LOW if store.settings.optimize_calendar_first else RATING.HIGH
