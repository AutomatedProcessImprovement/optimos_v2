from abc import ABC
from dataclasses import dataclass

from typing_extensions import Required

from o2.actions.base_actions.base_action import BaseAction, BaseActionParamsType
from o2.models.rule_selector import RuleSelector


class BatchingRuleBaseActionParamsType(BaseActionParamsType):
    """Base type for all action parameters."""

    rule: Required[RuleSelector]


@dataclass(frozen=True)
class BatchingRuleBaseAction(BaseAction, ABC, str=False):
    """Abstract class for all actions."""

    params: BaseActionParamsType
