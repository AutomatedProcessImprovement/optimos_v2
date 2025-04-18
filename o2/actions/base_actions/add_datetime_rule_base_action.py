from abc import ABC, abstractmethod
from dataclasses import dataclass, replace

from typing_extensions import NotRequired, Required, override

from o2.actions.base_actions.base_action import (
    BaseActionParamsType,
    RateSelfReturnType,
)
from o2.actions.base_actions.batching_rule_base_action import (
    BatchingRuleBaseAction,
)
from o2.models.constraints import RULE_TYPE
from o2.models.rule_selector import RuleSelector
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.settings import Settings
from o2.models.state import State
from o2.models.time_period import TimePeriod
from o2.models.timetable import (
    BatchingRule,
    FiringRule,
)
from o2.store import Store
from o2.util.logger import info


class AddDateTimeRuleBaseActionParamsType(BaseActionParamsType):
    """Parameter for AddDateTimeRuleBaseAction."""

    task_id: Required[str]
    time_period: Required[TimePeriod]
    duration_fn: Required[str]


@dataclass(frozen=True)
class AddDateTimeRuleBaseAction(BatchingRuleBaseAction, ABC, str=False):
    """AddDateTimeRuleBaseAction will add a new day of week and time of day rule."""

    params: AddDateTimeRuleBaseActionParamsType

    @override
    def apply(self, state: State, enable_prints: bool = True) -> State:
        timetable = state.timetable
        task_id = self.params["task_id"]
        time_period = self.params["time_period"]
        duration_fn = self.params.get("duration_fn", None)

        existing_task_rules = timetable.get_batching_rules_for_task(task_id)

        new_or_rule = [
            FiringRule.eq(RULE_TYPE.WEEK_DAY, time_period.from_),
            FiringRule.gte(RULE_TYPE.DAILY_HOUR, time_period.begin_time_hour),
            FiringRule.lt(RULE_TYPE.DAILY_HOUR, time_period.end_time_hour),
        ]
        if Settings.ADD_SIZE_RULE_TO_NEW_RULES:
            new_or_rule.append(FiringRule.gte(RULE_TYPE.SIZE, 2))

        if not existing_task_rules:
            # TODO: Allow combining rules, e.g. extending date range
            new_batching_rule = BatchingRule.from_task_id(
                task_id=task_id,
                firing_rules=new_or_rule,
                duration_fn=duration_fn,
            )
            return state.replace_timetable(batch_processing=timetable.batch_processing + [new_batching_rule])

        # Find the rule to modify
        rule = existing_task_rules[0]
        updated_rule = rule.add_firing_rules(new_or_rule)

        if enable_prints:
            info(
                f"\t\t>> Adding rule for {task_id} on {time_period.from_} from {time_period.begin_time} to {time_period.end_time}"
            )

        return replace(
            state,
            timetable=timetable.replace_batching_rule(
                RuleSelector.from_batching_rule(rule),
                updated_rule,
            ),
        )

    @override
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

    @override
    @override
    @staticmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        raise NotImplementedError("rate_self is not implemented")
