from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING

from o2.actions.base_actions.base_action import BaseAction, BaseActionParamsType
from o2.models.rule_selector import RuleSelector

if TYPE_CHECKING:
    from o2.store import State, Store


class BatchingRuleBaseActionParamsType(BaseActionParamsType):
    """Base type for all action parameters."""

    rule: RuleSelector


@dataclass(frozen=True)
class BatchingRuleBaseAction(BaseAction, ABC, str=False):
    """Abstract class for all actions."""

    params: BaseActionParamsType
