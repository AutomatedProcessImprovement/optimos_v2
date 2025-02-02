from abc import ABC, abstractmethod
from dataclasses import dataclass, replace
from typing import Literal

from sympy import Symbol, lambdify

from o2.actions.base_actions.base_action import (
    BaseAction,
    BaseActionParamsType,
    RateSelfReturnType,
)
from o2.actions.batching_rule_action import (
    BatchingRuleAction,
    BatchingRuleActionParamsType,
)
from o2.models.constraints import RULE_TYPE
from o2.models.days import DAY
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.state import State
from o2.models.time_period import TimePeriod
from o2.models.timetable import (
    BATCH_TYPE,
    COMPARATOR,
    BatchingRule,
    Distribution,
    FiringRule,
)
from o2.store import Store


class AddDateTimeRuleBaseActionParamsType(BaseActionParamsType):
    """Parameter for AddDateTimeRuleBaseAction."""

    task_id: str
    time_period: TimePeriod


@dataclass(frozen=True)
class AddDateTimeRuleBaseAction(BatchingRuleAction, ABC, str=False):
    """AddDateTimeRuleBaseAction will add a new day of week and time of day rule."""

    params: AddDateTimeRuleBaseActionParamsType

    def apply(self, state: State, enable_prints: bool = True) -> State:
        """Create a copy of the timetable with the rule size modified."""
        """Apply the action to the state."""
        timetable = state.timetable
        task_id = self.params["task_id"]
        time_period = self.params["time_period"]

        existing_task_rules = timetable.get_batching_rules_for_task(task_id)

        if not existing_task_rules:
            # TODO: Allow combining rules, e.g. extending date range
            new_batching_rule = BatchingRule(
                task_id=task_id,
                type=BATCH_TYPE.PARALLEL,
                size_distrib=[Distribution(key=str(1), value=0.0)]
                + [
                    Distribution(key=str(new_size), value=1.0)
                    for new_size in range(2, 100)
                ],
                duration_distrib=[
                    # TODO: Get duration from duration fn
                    Distribution(key=str(new_size), value=1 / new_size)
                    for new_size in range(1, 100)
                ],
                firing_rules=[
                    [
                        FiringRule(
                            attribute=RULE_TYPE.WEEK_DAY,
                            comparison=COMPARATOR.EQUAL,
                            value=time_period.from_,
                        ),
                        FiringRule(
                            attribute=RULE_TYPE.DAILY_HOUR,
                            comparison=COMPARATOR.GREATER_THEN_OR_EQUAL,
                            value=time_period.begin_time_hour,
                        ),
                        FiringRule(
                            attribute=RULE_TYPE.DAILY_HOUR,
                            comparison=COMPARATOR.LESS_THEN,
                            value=time_period.end_time_hour,
                        ),
                    ],
                ],
            )
            return state.replace_timetable(
                batch_processing=timetable.batch_processing + [new_batching_rule]
            )

        # Find the rule to modify
        rule = existing_task_rules[0]
        index = timetable.batch_processing.index(rule)

        new_or_rule = [
            FiringRule(
                attribute=RULE_TYPE.WEEK_DAY,
                comparison=COMPARATOR.EQUAL,
                value=time_period.from_,
            ),
            FiringRule(
                attribute=RULE_TYPE.DAILY_HOUR,
                comparison=COMPARATOR.GREATER_THEN_OR_EQUAL,
                value=time_period.begin_time_hour,
            ),
            FiringRule(
                attribute=RULE_TYPE.DAILY_HOUR,
                comparison=COMPARATOR.LESS_THEN,
                value=time_period.end_time_hour,
            ),
        ]
        updated_rule = replace(
            rule,
            firing_rules=rule.firing_rules + [new_or_rule],
        )

        if enable_prints:
            print(
                f"\t\t>> Adding rule for {task_id} on {time_period.from_} from {time_period.begin_time} to {time_period.end_time}"
            )

        return state.replace_timetable(
            batch_processing=timetable.batch_processing[:index]
            + [updated_rule]
            + timetable.batch_processing[index + 1 :],
        )

    @staticmethod
    @abstractmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        pass

    @staticmethod
    def get_default_rating() -> RATING:
        """Return the default rating for this action."""
        return RATING.MEDIUM


class AddDateTimeRuleAction(AddDateTimeRuleBaseAction):
    """AddDateTimeRuleAction will add a new day of week and time of day rule."""

    params: AddDateTimeRuleBaseActionParamsType

    @staticmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        raise NotImplementedError("rate_self is not implemented")
