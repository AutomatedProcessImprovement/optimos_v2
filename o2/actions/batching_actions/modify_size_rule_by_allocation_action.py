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


class ModifySizeRuleByAllocationActionParamsType(ModifySizeRuleBaseActionParamsType):
    """Parameter for ModifySizeRuleByAllocationAction."""

    pass


class ModifySizeRuleByLowAllocationAction(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on allocation.

    1. Gets tasks with high allocation ratio
        Allocation ratio = no. of resources assigned to the task / total no. of resources
    2. Looks at all resources with allocation high allocation ratio
    3. Gets a task (with batching enabled) that uses the resource
    4. Increases the size rule by 1
    """

    params: ModifySizeRuleByAllocationActionParamsType

    @staticmethod
    def rate_self(
        store: "Store", input: "Solution"
    ) -> RateSelfReturnType["ModifySizeRuleByLowAllocationAction | AddSizeRuleAction"]:
        """Generate a best set of parameters & self-evaluates this action."""
        timetable = input.state.timetable
        evaluation = input.evaluation

        resource_allocations = evaluation.resource_allocation_ratio_task
        tasks_by_allocation = sorted(resource_allocations.items(), key=lambda x: x[1], reverse=True)

        for task_id, _ in tasks_by_allocation:
            duration_fn = store.constraints.get_duration_fn_for_task(task_id)
            selectors = timetable.get_firing_rule_selectors_for_task(task_id, rule_type=RULE_TYPE.SIZE)
            # If no size rule exists, add one
            if not selectors:
                yield (
                    RATING.LOW,
                    AddSizeRuleAction(
                        AddSizeRuleBaseActionParamsType(task_id=task_id, size=2, duration_fn=duration_fn)
                    ),
                )
            for selector in select_variants(store, selectors):
                yield (
                    ModifySizeRuleBaseAction.get_default_rating(),
                    ModifySizeRuleByLowAllocationAction(
                        ModifySizeRuleByAllocationActionParamsType(
                            rule=selector,
                            size_increment=1,
                            duration_fn=duration_fn,
                        )
                    ),
                )


class ModifySizeRuleByHighAllocationAction(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on allocation.

    1. Gets tasks with low allocation ratio
        Allocation ratio = no. of resources assigned to the task / total no. of resources
    2. Looks at all resources with allocation low allocation ratio
    3. Gets a task (with batching enabled) that uses the resource
    4. Decreases the size rule by 1
    """

    params: ModifySizeRuleByAllocationActionParamsType

    @staticmethod
    def rate_self(
        store: "Store", input: "Solution"
    ) -> RateSelfReturnType["ModifySizeRuleByHighAllocationAction | AddSizeRuleAction"]:
        """Generate a best set of parameters & self-evaluates this action."""
        timetable = store.current_timetable
        evaluation = store.current_evaluation

        resource_allocations = evaluation.resource_allocation_ratio_task
        tasks_by_allocation = sorted(resource_allocations.items(), key=lambda x: x[1])

        for task_id, _ in tasks_by_allocation:
            selectors = timetable.get_firing_rule_selectors_for_task(task_id, rule_type=RULE_TYPE.SIZE)
            # NOTE: We do NOT try to add a new size rule here, because in this action we try to reduce batching
            for selector in select_variants(store, selectors):
                duration_fn = store.constraints.get_duration_fn_for_task(task_id)
                yield (
                    ModifySizeRuleBaseAction.get_default_rating(),
                    ModifySizeRuleByHighAllocationAction(
                        ModifySizeRuleByAllocationActionParamsType(
                            rule=selector,
                            size_increment=-1,
                            duration_fn=duration_fn,
                        )
                    ),
                )
