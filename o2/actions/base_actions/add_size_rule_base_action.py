from abc import ABC, abstractmethod
from dataclasses import dataclass, replace

from sympy import Symbol, lambdify
from typing_extensions import Required, override

from o2.actions.base_actions.base_action import (
    BaseAction,
    BaseActionParamsType,
    RateSelfReturnType,
)
from o2.models.constraints import RULE_TYPE
from o2.models.evaluation import Evaluation
from o2.models.rule_selector import RuleSelector
from o2.models.self_rating import RATING
from o2.models.state import State
from o2.models.timetable import (
    COMPARATOR,
    BatchingRule,
    Distribution,
    FiringRule,
)
from o2.store import Store
from o2.util.helper import select_variants


class AddSizeRuleBaseActionParamsType(BaseActionParamsType):
    """Parameter for ModifySizeRuleBaseAction."""

    size: Required[int]
    task_id: Required[str]
    duration_fn: Required[str]


@dataclass(frozen=True)
class AddSizeRuleBaseAction(BaseAction, ABC, str=False):
    """AddSizeRuleBaseAction will add a BatchingRule.

    This will effect the size distribution and the duration distribution of the rule,
    as well as the firing rule.
    """

    params: AddSizeRuleBaseActionParamsType

    @override
    def apply(self, state: State, enable_prints: bool = True) -> State:
        new_size = self.params["size"]
        task_id = self.params["task_id"]
        duration_fn = self.params.get("duration_fn", "1")

        duration_lambda = lambdify(Symbol("size"), duration_fn)

        timetable = state.timetable
        batching_rules = timetable.get_batching_rules_for_task(task_id)

        if new_size < 1:
            raise ValueError(f"Size must be at least 1, got {new_size}")

        # Make sure the size is at least 2, because 1 just means no batching
        batching_size = max(new_size, 2)

        # Create fully fresh rule
        if len(batching_rules) == 0:
            new_batching_rule = BatchingRule.from_task_id(
                task_id=task_id,
                firing_rules=[FiringRule.gte(RULE_TYPE.SIZE, batching_size)],
                duration_fn=duration_fn,
            )
            return state.replace_timetable(batch_processing=timetable.batch_processing + [new_batching_rule])
        # Add OR Case to existing rule
        else:
            existing_rule = batching_rules[0]
            # TODO: Check if a single size rule already exists, and if so, replace it
            new_batching_rule = replace(
                existing_rule,
                # Integrate in existing size distribution
                size_distrib=[
                    Distribution(key=str(batching_size), value=1.0),
                ]
                + [
                    size_distrib
                    for size_distrib in existing_rule.size_distrib
                    if size_distrib.key != str(batching_size)
                ],
                duration_distrib=[
                    Distribution(key=str(batching_size), value=duration_lambda(batching_size)),
                ]
                + [
                    duration_distrib
                    for duration_distrib in existing_rule.duration_distrib
                    if duration_distrib.key != str(batching_size)
                ],
                firing_rules=existing_rule.firing_rules
                + [
                    [FiringRule.gte(RULE_TYPE.SIZE, batching_size)],
                ],
            )
            new_timetable = timetable.replace_batching_rule(
                RuleSelector.from_batching_rule(new_batching_rule),
                new_batching_rule,
            )
            return replace(state, timetable=new_timetable)

    @override
    @staticmethod
    @abstractmethod
    def rate_self(store: Store, input: Evaluation) -> RateSelfReturnType:
        pass

    @staticmethod
    def get_default_rating() -> RATING:
        """Return the default rating for this action."""
        return RATING.MEDIUM


class AddSizeRuleAction(AddSizeRuleBaseAction):
    """AddSizeRuleAction will add a BatchingRule."""

    @override
    @override
    @staticmethod
    def rate_self(store: Store, input: Evaluation) -> RateSelfReturnType:
        task_ids = store.current_timetable.get_task_ids()

        for task_id in select_variants(store, task_ids):
            duration_fn = store.constraints.get_duration_fn_for_task(task_id)
            yield (
                RATING.VERY_LOW,
                AddSizeRuleAction(
                    AddSizeRuleBaseActionParamsType(
                        task_id=task_id,
                        size=2,
                        duration_fn=duration_fn,
                    )
                ),
            )
