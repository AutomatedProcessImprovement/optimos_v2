from o2.actions.base_actions.add_size_rule_base_action import (
    AddSizeRuleAction,
    AddSizeRuleBaseActionParamsType,
)
from o2.actions.base_actions.base_action import (
    RateSelfReturnType,
)
from o2.actions.base_actions.modify_size_rule_base_action import (
    ModifySizeRuleBaseAction,
    ModifySizeRuleBaseActionParamsType,
)
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.timetable import RULE_TYPE
from o2.store import Store


class ModifySizeRuleByCostActionParamsType(ModifySizeRuleBaseActionParamsType):
    """Parameter for ModifySizeRuleByCostAction."""

    pass


class ModifySizeRuleByCostAction(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on cost.

    1. Gets the tasks with the most cost
    2. Looks if theres a size rule for that task
    3. If there is, it increments the size by 1
    """

    params: ModifySizeRuleByCostActionParamsType

    @staticmethod
    def rate_self(
        store: "Store", input: SelfRatingInput
    ) -> RateSelfReturnType["ModifySizeRuleByCostAction | AddSizeRuleAction"]:
        """Generate a best set of parameters & self-evaluates this action."""
        timetable = store.current_timetable

        sorted_tasks = sorted(
            store.current_evaluation.get_avg_cost_per_task().items(),
            key=lambda x: x[1],
            reverse=True,
        )
        for task_id, _ in sorted_tasks:
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
                        ModifySizeRuleByCostAction(
                            ModifySizeRuleByCostActionParamsType(
                                rule=selector,
                                size_increment=1,
                                duration_fn=duration_fn,
                            )
                        ),
                    )
                # If nothing else helps, try to add a size rule
        for task_id, _ in sorted_tasks:
            yield (
                RATING.LOW,
                AddSizeRuleAction(
                    AddSizeRuleBaseActionParamsType(
                        task_id=task_id,
                        size=1,
                        duration_fn=store.constraints.get_duration_fn_for_task(task_id),
                    )
                ),
            )
