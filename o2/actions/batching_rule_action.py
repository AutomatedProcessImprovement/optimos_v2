from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Tuple, TypedDict

from o2.actions.base_action import BaseAction, BaseActionParamsType
from o2.types.rule_selector import RuleSelector

if TYPE_CHECKING:
    from o2.store import State, Store
from o2.types.self_rating import RATING, SelfRatingInput


class BatchingRuleActionParamsType(BaseActionParamsType):
    """Base type for all action parameters."""

    rule: RuleSelector


@dataclass(frozen=True)
class BatchingRuleAction(BaseAction):
    """Abstract class for all actions."""

    params: BaseActionParamsType
