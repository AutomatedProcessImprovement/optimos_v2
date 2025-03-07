import functools
from abc import ABC, abstractmethod
from collections.abc import Generator
from dataclasses import dataclass
from json import dumps
from typing import (
    TYPE_CHECKING,
    Optional,
    TypeVar,
)

from dataclass_wizard import JSONSerializable
from typing_extensions import TypedDict

from o2.util.helper import hash_string
from o2.util.logger import warn

if TYPE_CHECKING:
    from o2.models.self_rating import RATING, SelfRatingInput
    from o2.store import State, Store


ActionT = TypeVar("ActionT", bound="BaseAction")

ActionRatingTuple = tuple["RATING", Optional[ActionT]]

RateSelfReturnType = Generator[ActionRatingTuple[ActionT], bool, Optional[ActionRatingTuple[ActionT]]]


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
    def rate_self(store: "Store", input: "SelfRatingInput") -> RateSelfReturnType[ActionT]:
        """Generate a best set of parameters & self-evaluates this action."""
        pass

    def check_if_valid(self, store: "Store", mark_no_change_as_invalid: bool = False) -> bool:
        """Check if the action produces a valid state."""
        try:
            new_state = self.apply(store.current_state, enable_prints=False)
            if mark_no_change_as_invalid and new_state == store.current_state:
                return False
        except Exception as e:
            warn(f"Error applying action {self}: {e}")
            return False
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
        # Iterate over all params, sort them by name and concat them.
        return hash_string("|".join(f"{k}={v}" for k, v in sorted(self.params.items(), key=lambda x: x[0])))
