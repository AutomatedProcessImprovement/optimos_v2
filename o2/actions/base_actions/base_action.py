import functools
from abc import ABC, abstractmethod
from dataclasses import dataclass
from json import dumps
from typing import (
    TYPE_CHECKING,
    Generator,
    Optional,
    Tuple,
    TypeVar,
)

from dataclass_wizard import JSONSerializable
from typing_extensions import TypedDict

from o2.util.helper import hash_string

if TYPE_CHECKING:
    from o2.models.self_rating import RATING, SelfRatingInput
    from o2.store import State, Store


ActionT = TypeVar("ActionT", bound="BaseAction")

ActionRatingTuple = Tuple["RATING", Optional[ActionT]]

RateSelfReturnType = Generator[
    ActionRatingTuple[ActionT], bool, Optional[ActionRatingTuple[ActionT]]
]


class BaseActionParamsType(TypedDict):
    """Base type for all action parameters."""


@dataclass(frozen=True)
class BaseAction(JSONSerializable, ABC, str=False):
    """Abstract class for all actions."""

    params: BaseActionParamsType

    @abstractmethod
    def apply(self, state: "State", enable_prints: bool = True) -> "State":
        """Apply the action to the state, returning the new state."""
        pass

    @staticmethod
    @abstractmethod
    def rate_self(
        store: "Store", input: "SelfRatingInput"
    ) -> RateSelfReturnType[ActionT]:
        """Generate a best set of parameters & self-evaluates this action."""
        pass

    def check_if_valid(self, store: "Store") -> bool:
        """Check if the action produces a valid state."""
        new_state = self.apply(store.current_state, enable_prints=False)
        return (
            new_state.is_valid()
            and store.constraints.verify_legacy_constraints(new_state.timetable)
            and store.constraints.verify_batching_constraints(new_state.timetable)
        )

    def __str__(self) -> str:
        """Return a string representation of the action."""
        return f"{self.__class__.__name__}({self.params})"

    def __eq__(self, other: object) -> bool:
        """Check if two actions are equal."""
        if not isinstance(other, BaseAction):
            return NotImplemented
        return self.__class__ == other.__class__ and self.params == other.params

    @functools.cached_property
    def id(self) -> str:
        """Return a hash of the action."""
        return hash_string(dumps(self.to_json()))
