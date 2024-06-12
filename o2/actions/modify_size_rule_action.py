from sympy import Symbol, lambdify
from o2.actions.base_action import BaseAction, BaseActionParamsType
from o2.types.state import State
from o2.types.timetable import COMPARATOR, BatchingRule, Distribution, FiringRule
from o2.types.constraints import RULE_TYPE
from o2.store import Store
from o2.types.self_rating import RATING, SelfRatingInput

MARGIN_OF_ERROR = 0.03
SIZE_OF_CHANGE = 1


class ModifySizeRuleActionParamsType(BaseActionParamsType):
    size_increment: int
    duration_fn: str


class ModifySizeRuleAction(BaseAction):
    params: ModifySizeRuleActionParamsType

    # Returns a copy of the timetable with the rule size modified
    def apply(self, state: State, enable_prints=True):
        timetable = state.timetable
        rule_selector = self.params["rule"]

        (rule_index, old_rule) = timetable.get_batching_rule(rule_selector)
        if old_rule is None or rule_index is None:
            print(f"BatchingRule not found for {rule_selector}")
            return state
        old_size = self.get_dominant_distribution(old_rule).key
        new_size = int(old_size) + self.params["size_increment"]
        fn = lambdify(Symbol("size"), self.params["duration_fn"])
        size_distrib = [
            Distribution(
                key=str(1),
                value=0,
            ),
            Distribution(
                key=str(new_size),
                value=1,
            ),
        ]
        duration_distrib = [
            Distribution(
                key=str(new_size),
                value=fn(new_size),
            )
        ]

        # TODO: Do not replace the whole firing rules, just the one that needs to be changed
        firing_rules = [
            [
                FiringRule(
                    attribute=RULE_TYPE.SIZE,
                    comparison=COMPARATOR.EQUAL,
                    value=new_size,
                )
            ]
        ]
        newRule = BatchingRule(
            task_id=old_rule.task_id,
            type=old_rule.type,
            size_distrib=size_distrib,
            duration_distrib=duration_distrib,
            firing_rules=firing_rules,
        )

        if enable_prints:
            print(
                f"\t\t>> Modifying rule {old_rule.id()} to new size = {old_size} -> {new_size} & duration_modifier = {fn(new_size)}"
            )

        return state.replaceTimetable(
            batch_processing=timetable.batch_processing[:rule_index]
            + [newRule]
            + timetable.batch_processing[rule_index + 1 :],
        )

    def get_dominant_distribution(self, oldRule: BatchingRule):
        # Find the size distribution with the highest probability
        return max(
            oldRule.size_distrib,
            key=lambda distribution: distribution.value,
        )

    @staticmethod
    def rate_self(store: Store, input: SelfRatingInput):
        rule_selector = input.most_impactful_rule
        evaluation = input.most_impactful_rule_evaluation

        firing_rule = rule_selector.get_firing_rule_from_state(store.state)

        if firing_rule is None or firing_rule.attribute != RULE_TYPE.SIZE:
            return RATING.NOT_APPLICABLE, None

        # TODO Get current fastest evaluation by task
        base_evaluation = store.current_fastest_evaluation

        base_avg_wainting_time = base_evaluation.get_avg_waiting_time_of_task_id(
            rule_selector.batching_rule_task_id, store
        )
        new_avg_waiting_time = evaluation.get_avg_waiting_time_of_task_id(
            rule_selector.batching_rule_task_id, store
        )

        # This rule does reduce the waiting time, not increment it
        # TODO: We might want to try to increase the size of the rule,
        # but this only makes sense if we are looking for those positive rules
        # in the action_selector as well (see TODO there)
        if new_avg_waiting_time > base_avg_wainting_time:
            return RATING.NOT_APPLICABLE, None

        # If the change is only very small, we don't want to apply it
        if (1 - (new_avg_waiting_time / base_avg_wainting_time)) < MARGIN_OF_ERROR:
            return RATING.NOT_APPLICABLE, None

        constraints = store.constraints.get_batching_size_rule_constraints(
            rule_selector.batching_rule_task_id
        )

        max_allowed_min_size = max(
            [constraint.min_size for constraint in constraints], default=1
        )

        # Decrementing the size would break the constraints
        if (firing_rule.value - SIZE_OF_CHANGE) < max_allowed_min_size:
            return RATING.NOT_APPLICABLE, None

        return (
            RATING.MEDIUM,
            ModifySizeRuleAction(
                ModifySizeRuleActionParamsType(
                    size_increment=-1 * SIZE_OF_CHANGE,
                    duration_fn="size",
                    rule=rule_selector,
                )
            ),
        )
