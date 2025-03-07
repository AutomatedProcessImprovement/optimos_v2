from typing import Mapping

from o2.actions.base_actions.base_action import (
    RateSelfReturnType,
)
from o2.actions.base_actions.modify_size_rule_base_action import (
    ModifySizeRuleBaseAction,
    ModifySizeRuleBaseActionParamsType,
)
from o2.models.rule_selector import RuleSelector
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.timetable import RULE_TYPE
from o2.store import Store

LIMIT_OF_OPTIONS = 5


class ModifySizeRuleByCostFnParamsType(ModifySizeRuleBaseActionParamsType):
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

    sorted_metric_task_ids = sorted(
        task_id_metric_dict.keys(),
        key=lambda task_id: task_id_metric_dict[task_id],
        reverse=True,
    )[:LIMIT_OF_OPTIONS]
    for task_id in sorted_metric_task_ids:
        firing_rule_selectors = timetable.get_firing_rule_selectors_for_task(
            task_id, rule_type=RULE_TYPE.SIZE
        )
        if not firing_rule_selectors:
            continue

        size_constraints = constraints.get_batching_size_rule_constraints(task_id)
        if size_constraints is None:
            continue
        size_constraint = size_constraints[0]
        for firing_rule_selector in firing_rule_selectors:
            firing_rule = firing_rule_selector.get_firing_rule_from_state(state)
            if firing_rule is None:
                continue
            size = firing_rule.value

            new_cost = size_constraint.cost_fn_lambda(size + 1)
            old_cost = size_constraint.cost_fn_lambda(size)
            if new_cost < old_cost:
                yield (
                    ModifySizeRuleBaseAction.get_default_rating(),
                    task_class(
                        ModifySizeRuleByCostFnParamsType(
                            rule=firing_rule_selector,
                            size_increment=1,
                            duration_fn=size_constraint.duration_fn,
                        )
                    ),
                )


class ModifySizeRuleByCostFnRepetitiveTasks(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on the cost fn.

    If batch size increment reduces Costs => Increase Batch Size
    - For repetitive tasks (higher frequencies first)
    """

    params: ModifySizeRuleByCostFnParamsType

    @staticmethod
    def rate_self(
        store: "Store", input: SelfRatingInput
    ) -> RateSelfReturnType["ModifySizeRuleByCostFnRepetitiveTasks"]:
        """Generate a best set of parameters & self-evaluates this action."""
        evaluation = store.current_evaluation

        task_frequencies = evaluation.task_execution_counts
        yield from rate_self_helper_by_metric_dict(
            store, task_frequencies, ModifySizeRuleByCostFnRepetitiveTasks
        )


class ModifySizeRuleByCostFnHighCosts(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on the cost fn.

    If batch size increment reduces Costs => Increase Batch Size
    - For tasks with high costs (higher costs first).
    """

    params: ModifySizeRuleByCostFnParamsType

    @staticmethod
    def rate_self(
        store: "Store", input: SelfRatingInput
    ) -> RateSelfReturnType["ModifySizeRuleByCostFnHighCosts"]:
        """Generate a best set of parameters & self-evaluates this action."""
        evaluation = store.current_evaluation

        task_costs = evaluation.get_total_cost_per_task()
        yield from rate_self_helper_by_metric_dict(store, task_costs, ModifySizeRuleByCostFnHighCosts)


class ModifySizeRuleByCostFnLowProcessingTime(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on the cost fn.

    If batch size increment reduces processing time => Increase Batch Size
    - For tasks with low processing time (lower processing time first)
    """

    params: ModifySizeRuleByCostFnParamsType

    @staticmethod
    def rate_self(
        store: "Store", input: SelfRatingInput
    ) -> RateSelfReturnType["ModifySizeRuleByCostFnLowProcessingTime"]:
        """Generate a best set of parameters & self-evaluates this action."""
        evaluation = store.current_evaluation

        task_processing_times = evaluation.get_average_processing_time_per_task()
        yield from rate_self_helper_by_metric_dict(
            store, task_processing_times, ModifySizeRuleByCostFnLowProcessingTime
        )


class ModifyBatchSizeIfNoCostImprovement(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on the cost fn.

    If batch size decrement does not increase Costs (looking at the cost fn) => Decrease Batch Size

    NOTE: We do NOT limit the number of results here, because this action is
    also a fallback of sorts, so we make sure that every size rule is incremented
    if sensible.
    """

    params: ModifySizeRuleByCostFnParamsType

    @staticmethod
    def rate_self(
        store: "Store", input: SelfRatingInput
    ) -> RateSelfReturnType["ModifyBatchSizeIfNoCostImprovement"]:
        """Generate a best set of parameters & self-evaluates this action."""
        timetable = store.current_timetable
        constraints = store.constraints
        state = store.current_state

        task_ids = timetable.get_task_ids()
        task_costs: dict["RuleSelector", float] = {}

        for task_id in task_ids:
            firing_rule_selectors = timetable.get_firing_rule_selectors_for_task(
                task_id, rule_type=RULE_TYPE.SIZE
            )
            if not firing_rule_selectors:
                continue

            size_constraints = constraints.get_batching_size_rule_constraints(task_id)
            if size_constraints is None:
                continue
            size_constraint = size_constraints[0]
            for firing_rule_selector in firing_rule_selectors:
                firing_rule = firing_rule_selector.get_firing_rule_from_state(state)
                if firing_rule is None:
                    continue
                size = firing_rule.value

                new_cost = size_constraint.cost_fn_lambda(size - 1)
                old_cost = size_constraint.cost_fn_lambda(size)
                if new_cost <= old_cost:
                    task_costs[firing_rule_selector] = old_cost - new_cost

        sorted_task_costs = sorted(
            task_costs.keys(),
            key=lambda firing_rule_selector: task_costs[firing_rule_selector],
            reverse=True,
        )

        for rule_selector in sorted_task_costs:
            size_constraint = constraints.get_batching_size_rule_constraints(
                rule_selector.batching_rule_task_id
            )[0]

            yield (
                RATING.LOW,
                ModifyBatchSizeIfNoCostImprovement(
                    ModifySizeRuleByCostFnParamsType(
                        rule=rule_selector,
                        size_increment=1,
                        duration_fn=size_constraint.duration_fn,
                    )
                ),
            )


class ModifySizeRuleByCostFnLowCycleTimeImpact(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on the cost fn.

    If batch size increment reduces Costs => Increase Batch Size
    - For Tasks which have a low impact on the cycle time (looking at the duration fn)
    """

    params: ModifySizeRuleByCostFnParamsType

    @staticmethod
    def rate_self(
        store: "Store", input: SelfRatingInput
    ) -> RateSelfReturnType["ModifySizeRuleByCostFnLowCycleTimeImpact"]:
        """Generate a best set of parameters & self-evaluates this action."""
        timetable = store.current_timetable
        constraints = store.constraints
        state = store.current_state

        task_ids = timetable.get_task_ids()
        cycle_time_impacts: dict["RuleSelector", float] = {}

        for task_id in task_ids:
            firing_rule_selectors = timetable.get_firing_rule_selectors_for_task(
                task_id, rule_type=RULE_TYPE.SIZE
            )
            if not firing_rule_selectors:
                continue

            size_constraints = constraints.get_batching_size_rule_constraints(task_id)
            if size_constraints is None:
                continue
            size_constraint = size_constraints[0]
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
                    cycle_time_impacts[firing_rule_selector] = old_duration - new_duration

        sorted_cycle_time_impacts = sorted(
            cycle_time_impacts.keys(),
            key=lambda firing_rule_selector: cycle_time_impacts[firing_rule_selector],
            reverse=True,
        )[:LIMIT_OF_OPTIONS]

        for rule_selector in sorted_cycle_time_impacts:
            size_constraint = constraints.get_batching_size_rule_constraints(
                rule_selector.batching_rule_task_id
            )[0]

            yield (
                ModifySizeRuleBaseAction.get_default_rating(),
                ModifySizeRuleByCostFnLowCycleTimeImpact(
                    ModifySizeRuleByCostFnParamsType(
                        rule=rule_selector,
                        size_increment=1,
                        duration_fn=size_constraint.duration_fn,
                    )
                ),
            )


class ModifySizeRuleByManySimilarEnablements(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on the cost fn.

    - Modify those tasks, which have many enablements at the same time
    """

    params: ModifySizeRuleByCostFnParamsType

    @staticmethod
    def rate_self(
        store: "Store", input: SelfRatingInput
    ) -> RateSelfReturnType["ModifySizeRuleByManySimilarEnablements"]:
        """Generate a best set of parameters & self-evaluates this action."""
        evaluation = store.current_evaluation

        tasks_by_number_of_duplicate_enablement_dates = (
            evaluation.tasks_by_number_of_duplicate_enablement_dates
        )
        yield from rate_self_helper_by_metric_dict(
            store,
            tasks_by_number_of_duplicate_enablement_dates,
            ModifySizeRuleByManySimilarEnablements,
        )
