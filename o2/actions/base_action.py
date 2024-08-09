from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import (
    TYPE_CHECKING,
    Generator,
    Optional,
    Tuple,
    TypeAlias,
    TypedDict,
)

if TYPE_CHECKING:
    from o2.store import State, Store
from o2.models.self_rating import RATING, SelfRatingInput


ActionRatingTuple: TypeAlias = Tuple[RATING, Optional["BaseAction"]]
RateSelfReturnType = Generator[ActionRatingTuple, None, Optional[ActionRatingTuple]]


class BaseActionParamsType(TypedDict):
    """Base type for all action parameters."""


@dataclass(frozen=True)
class BaseAction(ABC):
    """Abstract class for all actions."""

    params: BaseActionParamsType

    @abstractmethod
    def apply(self, state: "State", enable_prints: bool = True) -> "State":
        """Apply the action to the state, returning the new state."""
        pass

    @staticmethod
    @abstractmethod
    def rate_self(store: "Store", input: SelfRatingInput) -> RateSelfReturnType:
        """Generate a best set of parameters & self-evaluates this action."""
        pass

    def __str__(self) -> str:
        """Return a string representation of the action."""
        return f"{self.__class__.__name__}({self.params})"

    def __eq__(self, other: object) -> bool:
        """Check if two actions are equal."""
        if not isinstance(other, BaseAction):
            return NotImplemented
        return self.__class__ == other.__class__ and self.params == other.params
