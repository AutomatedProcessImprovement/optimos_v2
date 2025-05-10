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
from o2.models.self_rating import RATING
from o2.models.solution import Solution
from o2.models.timetable import RULE_TYPE
from o2.store import Store
from o2.util.helper import select_variants


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
    def rate_self(
        store: "Store", input: "Solution"
    ) -> RateSelfReturnType["ModifySizeRuleByLowUtilizationAction | AddSizeRuleAction"]:
        """Generate a best set of parameters & self-evaluates this action."""
        timetable = input.state.timetable
        evaluation = input.evaluation

        resource_utilizations = evaluation.resource_utilizations
        resources_by_utilization = sorted(resource_utilizations.items(), key=lambda x: x[1])

        for resource_id, utilization in resources_by_utilization:
            if utilization > 0.5:
                continue

            tasks = timetable.get_task_ids_assigned_to_resource(resource_id)
            selectors = timetable.get_firing_rule_selectors_for_tasks(tasks, rule_type=RULE_TYPE.SIZE)
            if not selectors:
                for task_id in select_variants(store, tasks):
                    duration_fn = store.constraints.get_duration_fn_for_task(task_id)
                    yield (
                        RATING.LOW,
                        AddSizeRuleAction(
                            AddSizeRuleBaseActionParamsType(
                                task_id=task_id,
                                size=2,
                                duration_fn=duration_fn,
                            )
                        ),
                    )
                continue
            for selector in select_variants(store, selectors):
                duration_fn = store.constraints.get_duration_fn_for_task(selector.batching_rule_task_id)
                yield (
                    RATING.HIGH,
                    ModifySizeRuleByLowUtilizationAction(
                        ModifySizeRuleByUtilizationActionParamsType(
                            rule=selector,
                            size_increment=1,
                            duration_fn=duration_fn,
                        )
                    ),
                )


class ModifySizeRuleByHighUtilizationAction(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on utilization.

    1. Gets most utilized resources
    2. Looks at all resources with utilization > 0.8, largest utilization first
    3. Gets a task (with batching enabled) that uses the resource
    4. Reduces the size rule by 1
    """

    params: ModifySizeRuleByUtilizationActionParamsType

    @staticmethod
    def rate_self(
        store: "Store", input: "Solution"
    ) -> RateSelfReturnType["ModifySizeRuleByHighUtilizationAction"]:
        """Generate a best set of parameters & self-evaluates this action."""
        timetable = input.state.timetable
        evaluation = input.evaluation

        resource_utilizations = evaluation.resource_utilizations
        resources_by_utilization = sorted(resource_utilizations.items(), key=lambda x: x[1], reverse=True)

        for resource_id, utilization in resources_by_utilization:
            if utilization < 0.8:
                continue

            tasks = timetable.get_task_ids_assigned_to_resource(resource_id)
            selectors = timetable.get_firing_rule_selectors_for_tasks(tasks, rule_type=RULE_TYPE.SIZE)
            for selector in select_variants(store, selectors):
                duration_fn = store.constraints.get_duration_fn_for_task(selector.batching_rule_task_id)
                yield (
                    RATING.HIGH,
                    ModifySizeRuleByHighUtilizationAction(
                        ModifySizeRuleByUtilizationActionParamsType(
                            rule=selector,
                            size_increment=-1,
                            duration_fn=duration_fn,
                        )
                    ),
                )
