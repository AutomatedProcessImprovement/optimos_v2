from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Tuple, TypeVar, TypedDict

from o2.types.rule_selector import RuleSelector

if TYPE_CHECKING:
    from o2.store import Store, State
from o2.types.self_rating import RATING, SelfRatingInput


class BaseActionParamsType(TypedDict):
    rule: RuleSelector


@dataclass(frozen=True)
class BaseAction(ABC):
    params: BaseActionParamsType

    @abstractmethod
    def apply(self, state: "State", enable_prints=True) -> "State":
        pass

    @staticmethod
    @abstractmethod
    def rate_self(
        store: "Store", input: SelfRatingInput
    ) -> Tuple[RATING, Optional["BaseAction"]]:
        pass

    def __str__(self):
        return f"{self.__class__.__name__}({self.params})"

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.params == other.params
