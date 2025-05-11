from collections import defaultdict
from collections.abc import Mapping

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
from o2.models.rule_selector import RuleSelector
from o2.models.self_rating import RATING
from o2.models.solution import Solution
from o2.models.timetable import RULE_TYPE
from o2.store import Store
from o2.util.helper import select_variants


class ModifySizeRuleByCostFnActionParamsType(ModifySizeRuleBaseActionParamsType):
    """Parameter for ModifySizeRuleByCostFn."""

    pass


def rate_self_helper_by_metric_dict(
    store: "Store",
    task_id_metric_dict: Mapping[str, float],
    task_class: type[ModifySizeRuleBaseAction],
) -> RateSelfReturnType:
    """Rate ModifySizeRuleByCostFn actions."""
    timetable = store.current_timetable
    constraints = store.constraints
    state = store.current_state

    sorted_metric_values = sorted(set(task_id_metric_dict.values()), reverse=True)

    for metric in sorted_metric_values:
        task_ids = [task_id for task_id, value in task_id_metric_dict.items() if value == metric]
        for task_id in select_variants(store, task_ids):
            firing_rule_selectors = timetable.get_firing_rule_selectors_for_task(
                task_id, rule_type=RULE_TYPE.SIZE
            )
            size_constraints = constraints.get_batching_size_rule_constraints(task_id)
            if not size_constraints:
                continue
            size_constraint = size_constraints[0]

            # In case we do not have firing_rule selectors, we might want to add a new rule
            if not firing_rule_selectors:
                new_cost = size_constraint.cost_fn_lambda(2)
                old_cost = size_constraint.cost_fn_lambda(1)
                if new_cost <= old_cost:
                    duration_fn = store.constraints.get_duration_fn_for_task(task_id)
                    yield (
                        RATING.LOW,
                        AddSizeRuleAction(
                            AddSizeRuleBaseActionParamsType(task_id=task_id, size=2, duration_fn=duration_fn)
                        ),
                    )

            for firing_rule_selector in select_variants(store, firing_rule_selectors, inner=True):
                firing_rule = firing_rule_selector.get_firing_rule_from_state(state)
                if firing_rule is None:
                    continue
                size = firing_rule.value

                new_cost = size_constraint.cost_fn_lambda(size + 1)
                old_cost = size_constraint.cost_fn_lambda(size)
                if new_cost <= old_cost:
                    yield (
                        ModifySizeRuleBaseAction.get_default_rating(),
                        task_class(
                            ModifySizeRuleByCostFnActionParamsType(
                                rule=firing_rule_selector,
                                size_increment=1,
                                duration_fn=size_constraint.duration_fn,
                            )
                        ),
                    )


class ModifySizeRuleByCostFnRepetitiveTasksAction(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on the cost fn.

    If batch size increment reduces Costs => Increase Batch Size
    - For repetitive tasks (higher frequencies first)
    """

    params: ModifySizeRuleByCostFnActionParamsType

    @staticmethod
    def rate_self(
        store: "Store", input: "Solution"
    ) -> RateSelfReturnType["ModifySizeRuleByCostFnRepetitiveTasksAction"]:
        """Generate a best set of parameters & self-evaluates this action."""
        evaluation = input.evaluation

        task_frequencies = evaluation.task_execution_counts
        yield from rate_self_helper_by_metric_dict(
            store, task_frequencies, ModifySizeRuleByCostFnRepetitiveTasksAction
        )


class ModifySizeRuleByCostFnHighCostsAction(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on the cost fn.

    If batch size increment reduces Costs => Increase Batch Size
    - For tasks with high costs (higher costs first).
    """

    params: ModifySizeRuleByCostFnActionParamsType

    @staticmethod
    def rate_self(
        store: "Store", input: "Solution"
    ) -> RateSelfReturnType["ModifySizeRuleByCostFnHighCostsAction"]:
        """Generate a best set of parameters & self-evaluates this action."""
        evaluation = input.evaluation

        task_costs = evaluation.get_total_cost_per_task()
        yield from rate_self_helper_by_metric_dict(store, task_costs, ModifySizeRuleByCostFnHighCostsAction)


class ModifySizeRuleByCostFnLowProcessingTimeAction(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on the cost fn.

    If batch size increment reduces processing time => Increase Batch Size
    - For tasks with low processing time (lower processing time first)
    """

    params: ModifySizeRuleByCostFnActionParamsType

    @staticmethod
    def rate_self(
        store: "Store", input: "Solution"
    ) -> RateSelfReturnType["ModifySizeRuleByCostFnLowProcessingTimeAction"]:
        """Generate a best set of parameters & self-evaluates this action."""
        evaluation = input.evaluation

        task_processing_times = evaluation.get_average_processing_time_per_task()
        yield from rate_self_helper_by_metric_dict(
            store, task_processing_times, ModifySizeRuleByCostFnLowProcessingTimeAction
        )


class ModifyBatchSizeIfNoCostImprovementAction(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on the cost fn.

    If batch size decrement does not increase Costs (looking at the cost fn) => Decrease Batch Size
    """

    params: ModifySizeRuleByCostFnActionParamsType

    @staticmethod
    def rate_self(
        store: "Store", input: "Solution"
    ) -> RateSelfReturnType["ModifyBatchSizeIfNoCostImprovementAction | AddSizeRuleAction"]:
        """Generate a best set of parameters & self-evaluates this action."""
        constraints = store.constraints
        timetable = input.state.timetable
        state = input.state

        task_ids = timetable.get_task_ids()
        rule_selectors_by_cost: dict[float, list[RuleSelector]] = defaultdict(list)

        for task_id in task_ids:
            size_constraints = constraints.get_batching_size_rule_constraints(task_id)
            if not size_constraints:
                continue
            size_constraint = size_constraints[0]

            firing_rule_selectors = timetable.get_firing_rule_selectors_for_task(
                task_id, rule_type=RULE_TYPE.SIZE
            )

            # Because we are aiming to reduce batch size, we do NOT add a new rule here
            if not firing_rule_selectors:
                continue

            for firing_rule_selector in firing_rule_selectors:
                firing_rule = firing_rule_selector.get_firing_rule_from_state(state)
                if firing_rule is None:
                    continue
                size = firing_rule.value

                new_cost = size_constraint.cost_fn_lambda(size - 1)
                old_cost = size_constraint.cost_fn_lambda(size)
                if new_cost <= old_cost:
                    cost = old_cost - new_cost
                    rule_selectors_by_cost[cost].append(firing_rule_selector)

        costs_sorted = sorted(rule_selectors_by_cost.keys(), reverse=True)

        for cost in costs_sorted:
            rule_selectors = rule_selectors_by_cost[cost]
            for rule_selector in select_variants(store, rule_selectors):
                duration_fn = constraints.get_duration_fn_for_task(rule_selector.batching_rule_task_id)
                yield (
                    RATING.LOW,
                    ModifyBatchSizeIfNoCostImprovementAction(
                        ModifySizeRuleByCostFnActionParamsType(
                            rule=rule_selector,
                            size_increment=-1,
                            duration_fn=duration_fn,
                        )
                    ),
                )


class ModifySizeRuleByCostFnLowCycleTimeImpactAction(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on the cost fn.

    If batch size increment reduces Costs => Increase Batch Size
    - For Tasks which have a low impact on the cycle time (looking at the duration fn)
    """

    params: ModifySizeRuleByCostFnActionParamsType

    @staticmethod
    def rate_self(
        store: "Store", input: "Solution"
    ) -> RateSelfReturnType["ModifySizeRuleByCostFnLowCycleTimeImpactAction | AddSizeRuleAction"]:
        """Generate a best set of parameters & self-evaluates this action."""
        timetable = input.state.timetable
        constraints = store.constraints
        state = input.state

        task_ids = timetable.get_task_ids()
        rule_selectors_by_cycle_time_impact: dict[float, list[RuleSelector]] = defaultdict(list)

        for task_id in task_ids:
            size_constraints = constraints.get_batching_size_rule_constraints(task_id)
            if not size_constraints:
                continue
            size_constraint = size_constraints[0]

            firing_rule_selectors = timetable.get_firing_rule_selectors_for_task(
                task_id, rule_type=RULE_TYPE.SIZE
            )
            if not firing_rule_selectors:
                new_cost = size_constraint.cost_fn_lambda(2)
                old_cost = size_constraint.cost_fn_lambda(1)

                old_duration = size_constraint.duration_fn_lambda(1)
                new_duration = size_constraint.duration_fn_lambda(2)
                if new_cost < old_cost:
                    cycle_time_impact = old_duration - new_duration
                    rule_selectors_by_cycle_time_impact[cycle_time_impact].append(
                        RuleSelector(batching_rule_task_id=task_id, firing_rule_index=None)
                    )

            for firing_rule_selector in firing_rule_selectors:
                firing_rule = firing_rule_selector.get_firing_rule_from_state(state)
                if firing_rule is None:
                    continue
                size = firing_rule.value

                new_cost = size_constraint.cost_fn_lambda(size + 1)
                old_cost = size_constraint.cost_fn_lambda(size)

                old_duration = size_constraint.duration_fn_lambda(size)
                new_duration = size_constraint.duration_fn_lambda(size + 1)
                if new_cost < old_cost:
                    cycle_time_impact = old_duration - new_duration
                    rule_selectors_by_cycle_time_impact[cycle_time_impact].append(firing_rule_selector)

        cycle_time_impacts_sorted = sorted(
            rule_selectors_by_cycle_time_impact.keys(),
            reverse=True,
        )

        for cycle_time_impact in cycle_time_impacts_sorted:
            rule_selectors = rule_selectors_by_cycle_time_impact[cycle_time_impact]
            for rule_selector in select_variants(store, rule_selectors):
                duration_fn = constraints.get_duration_fn_for_task(rule_selector.batching_rule_task_id)

                if rule_selector.firing_rule_index is not None:
                    yield (
                        ModifySizeRuleBaseAction.get_default_rating(),
                        ModifySizeRuleByCostFnLowCycleTimeImpactAction(
                            ModifySizeRuleByCostFnActionParamsType(
                                rule=rule_selector,
                                size_increment=1,
                                duration_fn=duration_fn,
                            )
                        ),
                    )
                else:
                    yield (
                        RATING.LOW,
                        AddSizeRuleAction(
                            AddSizeRuleBaseActionParamsType(
                                task_id=rule_selector.batching_rule_task_id,
                                size=2,
                                duration_fn=duration_fn,
                            )
                        ),
                    )


class ModifySizeRuleByManySimilarEnablementsAction(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on the cost fn.

    - Modify those tasks, which have many enablements at the same time
    """

    params: ModifySizeRuleByCostFnActionParamsType

    @staticmethod
    def rate_self(
        store: "Store", input: "Solution"
    ) -> RateSelfReturnType["ModifySizeRuleByManySimilarEnablementsAction"]:
        """Generate a best set of parameters & self-evaluates this action."""
        evaluation = input.evaluation

        tasks_by_number_of_duplicate_enablement_dates = (
            evaluation.tasks_by_number_of_duplicate_enablement_dates
        )
        yield from rate_self_helper_by_metric_dict(
            store,
            tasks_by_number_of_duplicate_enablement_dates,
            ModifySizeRuleByManySimilarEnablementsAction,
        )
