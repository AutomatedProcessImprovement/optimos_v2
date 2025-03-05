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


class ModifySizeRuleByDurationFnParamsType(ModifySizeRuleBaseActionParamsType):
    """Parameter for ModifySizeRuleByCostFn."""

    pass


class ModifyBatchSizeIfNoDurationImprovement(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on the cost fn.

    If batch size decrement does not increase Duration (looking at the duration fn) => Decrease Batch Size

    NOTE: We do NOT limit the number of results here, because this action is
    also a fallback of sorts, so we make sure that every size rule is incremented
    if sensible.
    """

    params: ModifySizeRuleByDurationFnParamsType

    @staticmethod
    def rate_self(
        store: "Store", input: SelfRatingInput
    ) -> RateSelfReturnType["ModifyBatchSizeIfNoDurationImprovement"]:
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

                new_duration = size_constraint.duration_fn_lambda(size - 1)
                old_duration = size_constraint.duration_fn_lambda(size)
                if new_duration <= old_duration:
                    task_costs[firing_rule_selector] = old_duration - new_duration

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
                ModifyBatchSizeIfNoDurationImprovement(
                    ModifySizeRuleByDurationFnParamsType(
                        rule=rule_selector,
                        size_increment=-1,
                        duration_fn=size_constraint.duration_fn,
                    )
                ),
            )


class ModifySizeRuleByDurationFnCostImpact(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on the duration fn.

    If batch size increment reduces Duration => Increase Batch Size
    - Sorted by the cost impact of that size increment.

    NOTE: We do NOT limit the number of results here, because this action is
    also a fallback of sorts, so we make sure that every size rule is incremented
    if sensible.
    """

    params: ModifySizeRuleByDurationFnParamsType

    @staticmethod
    def rate_self(
        store: "Store", input: SelfRatingInput
    ) -> RateSelfReturnType["ModifySizeRuleByDurationFnCostImpact"]:
        """Generate a best set of parameters & self-evaluates this action."""
        timetable = store.current_timetable
        constraints = store.constraints
        state = store.current_state

        task_ids = timetable.get_task_ids()
        duration_impacts: dict["RuleSelector", float] = {}

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

                old_duration = size_constraint.duration_fn_lambda(size)
                new_duration = size_constraint.duration_fn_lambda(size + 1)

                old_cost = size_constraint.cost_fn_lambda(size)
                new_cost = size_constraint.cost_fn_lambda(size + 1)
                if new_duration < old_duration:
                    duration_impacts[firing_rule_selector] = old_cost - new_cost

        sorted_duration_impacts = sorted(
            duration_impacts.keys(),
            key=lambda firing_rule_selector: duration_impacts[firing_rule_selector],
            reverse=True,
        )

        for rule_selector in sorted_duration_impacts:
            size_constraint = constraints.get_batching_size_rule_constraints(
                rule_selector.batching_rule_task_id
            )[0]

            yield (
                RATING.LOW,
                ModifySizeRuleByDurationFnCostImpact(
                    ModifySizeRuleByDurationFnParamsType(
                        rule=rule_selector,
                        size_increment=1,
                        duration_fn=size_constraint.duration_fn,
                    )
                ),
            )
