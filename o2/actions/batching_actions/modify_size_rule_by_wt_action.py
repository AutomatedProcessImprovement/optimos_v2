from o2.actions.base_actions.base_action import (
    RateSelfReturnType,
)
from o2.actions.base_actions.modify_size_rule_base_action import (
    ModifySizeRuleBaseAction,
    ModifySizeRuleBaseActionParamsType,
)
from o2.models.self_rating import SelfRatingInput
from o2.models.timetable import RULE_TYPE
from o2.store import Store

LIMIT_OF_OPTIONS = 5


class ModifySizeRuleByWTActionParamsType(ModifySizeRuleBaseActionParamsType):
    """Parameter for ModifySizeRuleByWTAction."""

    pass


class ModifySizeRuleByWTAction(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on waiting time.

    1. Gets the tasks with the most waiting time
    2. Looks if theres a size rule for that task
    3. If there is, it decrements the size by 1
    """

    params: ModifySizeRuleByWTActionParamsType

    @staticmethod
    def rate_self(
        store: "Store", input: SelfRatingInput
    ) -> RateSelfReturnType["ModifySizeRuleByWTAction"]:
        """Generate a best set of parameters & self-evaluates this action."""
        timetable = store.current_timetable
        avg_batching_waiting_time_per_task = (
            store.current_evaluation.avg_batching_waiting_time_per_task
        )
        sorted_tasks = sorted(
            avg_batching_waiting_time_per_task.items(),
            key=lambda x: x[1],
            reverse=True,
        )[:LIMIT_OF_OPTIONS]
        for task_id, waiting_time in sorted_tasks:
            if (waiting_time) <= 0:
                continue
            batching_rules = timetable.get_batching_rules_for_task(task_id)
            for batching_rule in batching_rules:
                selectors = batching_rule.get_firing_rule_selectors(type=RULE_TYPE.SIZE)
                for selector in selectors:
                    constraints = store.constraints.get_batching_size_rule_constraints(
                        task_id
                    )
                    duration_fn = "1" if not constraints else constraints[0].duration_fn
                    yield (
                        ModifySizeRuleBaseAction.get_default_rating(),
                        ModifySizeRuleByWTAction(
                            ModifySizeRuleByWTActionParamsType(
                                rule=selector,
                                size_increment=-1,
                                duration_fn=duration_fn,
                            )
                        ),
                    )
