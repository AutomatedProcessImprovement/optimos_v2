from typing import Generator, Mapping

from o2.actions.base_action import BaseAction, BaseActionParamsType, RateSelfReturnType
from o2.actions.modify_size_rule_base_action import (
    ModifySizeRuleBaseAction,
    ModifySizeRuleBaseActionParamsType,
)
from o2.models.rule_selector import RuleSelector
from o2.models.self_rating import SelfRatingInput
from o2.models.timetable import RULE_TYPE
from o2.store import Store


class ModifySizeRuleByCostFnParamsType(ModifySizeRuleBaseActionParamsType):
    """Parameter for ModifySizeRuleByCostFn."""

    pass


def rate_self_helper_by_metric_dict(
    store: "Store",
    task_id_metric_dict: Mapping[str, float],
    task_class: type[ModifySizeRuleBaseAction],
) -> RateSelfReturnType:
    """Helper function to rate ModifySizeRuleByCostFn actions."""
    timetable = store.current_timetable
    constraints = store.constraints
    state = store.current_state

    sorted_metric_task_ids = sorted(
        task_id_metric_dict.keys(),
        key=lambda task_id: task_id_metric_dict[task_id],
        reverse=True,
    )
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
    def rate_self(store: "Store", input: SelfRatingInput) -> RateSelfReturnType:
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
    def rate_self(store: "Store", input: SelfRatingInput) -> RateSelfReturnType:
        """Generate a best set of parameters & self-evaluates this action."""
        evaluation = store.current_evaluation

        task_costs = evaluation.get_total_cost_per_task()
        yield from rate_self_helper_by_metric_dict(
            store, task_costs, ModifySizeRuleByCostFnHighCosts
        )


class ModifySizeRuleByCostFnLowCycleTimeImpact(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on the cost fn.

    If batch size increment reduces Costs => Increase Batch Size
    - For Tasks which have a low impact on the cycle time.
    """

    params: ModifySizeRuleByCostFnParamsType

    @staticmethod
    def rate_self(store: "Store", input: SelfRatingInput) -> RateSelfReturnType:
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
                if new_cost < old_cost:
                    cycle_time_impacts[firing_rule_selector] = (
                        size_constraint.duration_fn_lambda(size)
                        - size_constraint.duration_fn_lambda(size + 1)
                    )

        sorted_cycle_time_impacts = sorted(
            cycle_time_impacts.keys(),
            key=lambda firing_rule_selector: cycle_time_impacts[firing_rule_selector],
            reverse=True,
        )

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
