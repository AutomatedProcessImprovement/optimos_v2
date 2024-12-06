from o2.actions.base_actions.base_action import (
    BaseAction,
    BaseActionParamsType,
    RateSelfReturnType,
)
from o2.actions.base_actions.modify_size_rule_base_action import (
    ModifySizeRuleBaseAction,
    ModifySizeRuleBaseActionParamsType,
)
from o2.models.self_rating import SelfRatingInput
from o2.models.timetable import RULE_TYPE
from o2.store import Store


class ModifySizeRuleByUtilizationActionParamsType(ModifySizeRuleBaseActionParamsType):
    """Parameter for ModifySizeRuleByUtilizationAction."""

    pass


class ModifySizeRuleByLowUtilizationAction(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on utilization.

    1. Gets least utilized resources
    2. Looks at all resources with utilization < 0.5, smallest utilization first
    3. Gets a task (with batching enabled) that uses the resource
    4. Increases the size rule by 1
    """

    params: ModifySizeRuleByUtilizationActionParamsType

    @staticmethod
    def rate_self(store: "Store", input: SelfRatingInput) -> RateSelfReturnType:
        """Generate a best set of parameters & self-evaluates this action."""
        timetable = store.current_timetable
        evaluation = store.current_evaluation

        resource_utilizations = evaluation.resource_utilizations
        resources_by_utilization = sorted(
            resource_utilizations.items(), key=lambda x: x[1]
        )

        for resource_id, utilization in resources_by_utilization:
            if utilization > 0.5:
                continue

            tasks = timetable.get_task_ids_assigned_to_resource(resource_id)
            for task_id in tasks:
                batching_rules = timetable.get_batching_rules_for_task(task_id)
                for batching_rule in batching_rules:
                    selectors = batching_rule.get_firing_rule_selectors(
                        type=RULE_TYPE.SIZE
                    )
                    for selector in selectors:
                        constraints = (
                            store.constraints.get_batching_size_rule_constraints(
                                task_id
                            )
                        )
                        duration_fn = (
                            "1" if not constraints else constraints[0].duration_fn
                        )
                        yield (
                            ModifySizeRuleBaseAction.get_default_rating(),
                            ModifySizeRuleByLowUtilizationAction(
                                ModifySizeRuleByUtilizationActionParamsType(
                                    rule=selector,
                                    size_increment=1,
                                    duration_fn=duration_fn,
                                )
                            ),
                        )


