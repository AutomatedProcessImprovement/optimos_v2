from dataclasses import dataclass
from typing import TypedDict
from optimos_v2.src.types.state import State


class BaseActionParamsType(TypedDict):
    pass


@dataclass(frozen=True)
class BaseAction:
    params: BaseActionParamsType

    def apply(self, state: State, enable_prints=True) -> State:
        raise NotImplementedError

    def __str__(self):
        return f"{self.__class__.__name__}({self.params})"

    def __eq__(self, other):
        return self.__class__ == other.__class__ and self.params == other.params

