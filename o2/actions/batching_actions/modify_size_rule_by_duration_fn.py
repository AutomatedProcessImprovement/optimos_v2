from collections import defaultdict

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
from o2.util.helper import select_variants


class ModifySizeRuleByDurationFnParamsType(ModifySizeRuleBaseActionParamsType):
    """Parameter for ModifySizeRuleByCostFn."""

    pass


class ModifyBatchSizeIfNoDurationImprovement(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on the cost fn.

    If batch size decrement does not increase Duration (looking at the duration fn) => Decrease Batch Size
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
        rule_selectors_by_duration: dict[float, list[RuleSelector]] = defaultdict(list)

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
                    rule_selectors_by_duration[old_duration - new_duration].append(firing_rule_selector)

        sorted_rule_selectors = sorted(
            rule_selectors_by_duration.keys(),
            key=lambda duration: rule_selectors_by_duration[duration],
            reverse=True,
        )

        for duration in sorted_rule_selectors:
            rule_selectors = rule_selectors_by_duration[duration]
            for rule_selector in select_variants(store, rule_selectors):
                duration_fn = constraints.get_duration_fn_for_task(rule_selector.batching_rule_task_id)

                yield (
                    RATING.LOW,
                    ModifyBatchSizeIfNoDurationImprovement(
                        ModifySizeRuleByDurationFnParamsType(
                            rule=rule_selector,
                            size_increment=-1,
                            duration_fn=duration_fn,
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
        rule_selectors_by_duration: dict[float, list[RuleSelector]] = defaultdict(list)

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
                if new_duration <= old_duration:
                    rule_selectors_by_duration[old_cost - new_cost].append(firing_rule_selector)

        sorted_rule_selectors = sorted(
            rule_selectors_by_duration.keys(),
            key=lambda duration: rule_selectors_by_duration[duration],
            reverse=True,
        )

        for duration in sorted_rule_selectors:
            rule_selectors = rule_selectors_by_duration[duration]
            for rule_selector in select_variants(store, rule_selectors):
                duration_fn = constraints.get_duration_fn_for_task(rule_selector.batching_rule_task_id)

                yield (
                    RATING.LOW,
                    ModifySizeRuleByDurationFnCostImpact(
                        ModifySizeRuleByDurationFnParamsType(
                            rule=rule_selector,
                            size_increment=1,
                            duration_fn=duration_fn,
                        )
                    ),
                )
