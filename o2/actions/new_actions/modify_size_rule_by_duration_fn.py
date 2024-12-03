
class ModifyBatchSizeIfNoDurationImprovement(ModifySizeRuleBaseAction):
    """An Action to modify size batching rules based on the cost fn.

    If batch size decrement does not increase Duration (looking at the duration fn) => Decrease Batch Size
    """

    params: ModifySizeRuleByDurationFnParamsType

    @staticmethod
    def rate_self(store: "Store", input: SelfRatingInput) -> RateSelfReturnType:
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
                RATING.HIGH,
                ModifyBatchSizeIfNoDurationImprovement(
                    ModifySizeRuleByDurationFnParamsType(
                        rule=rule_selector,
                        size_increment=1,
                        duration_fn=size_constraint.duration_fn,
                    )
                ),
            )


