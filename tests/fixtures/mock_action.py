from dataclasses import dataclass, field

from o2.actions.base_action import BaseAction, BaseActionParamsType
from o2.models.self_rating import RATING
from o2.util.helper import random_string


class MockActionParamsType(BaseActionParamsType):
    random_string: str
    pass


@dataclass(frozen=True)
class MockAction(BaseAction):
    params: MockActionParamsType = field(
        default_factory=lambda: MockActionParamsType(random_string=random_string())
    )
    pass

    def apply(self, state, enable_prints=True):
        return state

    @staticmethod
    def rate_self(store, input):
        yield RATING.NOT_APPLICABLE, None
        return