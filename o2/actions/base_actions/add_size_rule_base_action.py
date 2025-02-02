from abc import ABC, abstractmethod
from dataclasses import dataclass, replace

from o2.actions.base_actions.base_action import (
    BaseAction,
    BaseActionParamsType,
    RateSelfReturnType,
)
from o2.models.constraints import RULE_TYPE
from o2.models.rule_selector import RuleSelector
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.state import State
from o2.models.timetable import (
    COMPARATOR,
    BatchingRule,
    Distribution,
    FiringRule,
)
from o2.store import Store


class AddSizeRuleBaseActionParamsType(BaseActionParamsType):
    """Parameter for ModifySizeRuleBaseAction."""

    size: int
    task_id: str


@dataclass(frozen=True)
class AddSizeRuleBaseAction(BaseAction, ABC, str=False):
    """AddSizeRuleBaseAction will add a BatchingRule.

    This will effect the size distribution and the duration distribution of the rule,
    as well as the firing rule.
    """

    params: AddSizeRuleBaseActionParamsType

    def apply(self, state: State, enable_prints: bool = True) -> State:
        """Create a copy of the timetable with the rule size modified."""

        new_size = self.params["size"]
        task_id = self.params["task_id"]

        timetable = state.timetable
        batching_rules = timetable.get_batching_rules_for_task(task_id)

        # Create fully fresh rule
        if len(batching_rules) == 0:
            new_batching_rule = BatchingRule.from_task_id(
                task_id=task_id,
                size=new_size,
                firing_rules=[FiringRule.gte(RULE_TYPE.SIZE, new_size)],
            )
            return state.replace_timetable(
                batch_processing=timetable.batch_processing + [new_batching_rule]
            )
        # Add OR Case to existing rule
        else:
            existing_rule = batching_rules[0]
            # TODO: Check if a single size rule already exists, and if so, replace it
            new_batching_rule = replace(
                existing_rule,
                # Integrate in existing size distribution
                size_distrib=[
                    Distribution(key=str(new_size), value=1.0),
                ]
                + [
                    size_distrib
                    for size_distrib in existing_rule.size_distrib
                    if size_distrib.key != str(new_size)
                ],
                duration_distrib=[
                    # TODO: Get duration from duration fn
                    Distribution(key=str(new_size), value=1 / new_size),
                ]
                + [
                    duration_distrib
                    for duration_distrib in existing_rule.duration_distrib
                ],
                firing_rules=existing_rule.firing_rules
                + [
                    [FiringRule.gte(RULE_TYPE.SIZE, new_size)],
                ],
            )
            new_timetable = timetable.replace_batching_rule(
                RuleSelector.from_batching_rule(new_batching_rule),
                new_batching_rule,
            )
            return replace(state, timetable=new_timetable)

    @staticmethod
    @abstractmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        pass

    @staticmethod
    def get_default_rating() -> RATING:
        """Return the default rating for this action."""
        return RATING.MEDIUM


class AddSizeRuleAction(AddSizeRuleBaseAction):
    """AddSizeRuleAction will add a BatchingRule."""

    @staticmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        raise NotImplementedError("Not implemented")
