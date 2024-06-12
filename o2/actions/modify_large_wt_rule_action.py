from o2.actions.base_action import BaseAction, BaseActionParamsType
from o2.types.state import State
from o2.types.timetable import COMPARATOR, BatchingRule, FiringRule, rule_is_large_wt
from o2.types.constraints import RULE_TYPE
from o2.store import Store
from o2.types.self_rating import RATING, SelfRatingInput

SIZE_OF_CHANGE = 100
CLOSENESS_TO_MAX_WT = 0.01


class ModifyLargeWtRuleActionParamsType(BaseActionParamsType):
    wt_increment: int


class ModifyLargeWtRuleAction(BaseAction):
    params: ModifyLargeWtRuleActionParamsType

    # Returns a copy of the timetable with the rule size modified
    def apply(self, state: State, enable_prints=True):
        timetable = state.timetable
        rule_selector = self.params["rule"]
        wt_increment = self.params["wt_increment"]

        index, rule = timetable.get_batching_rule(rule_selector)
        if rule is None or index is None:
            print(f"BatchingRule not found for {rule_selector}")
            return state

        firing_rule = rule.get_firing_rule(rule_selector)
        if not rule_is_large_wt(firing_rule):
            print(f"Firing rule not found for {rule_selector}")
            return state

        old_wt = firing_rule.value
        new_wt = old_wt + wt_increment

        new_firing_rule = FiringRule(
            attribute=RULE_TYPE.LARGE_WT,
            comparison=COMPARATOR.EQUAL,
            value=new_wt,
        )

        new_batching_rule = rule.replace_firing_rule(rule_selector, new_firing_rule)

        return state.replaceTimetable(
            batch_processing=timetable.batch_processing[:index]
            + [new_batching_rule]
            + timetable.batch_processing[index + 1 :],
        )

    @staticmethod
    def rate_self(store: Store, input: SelfRatingInput):
        rule_selector = input.most_impactful_rule
        base_evaluation = store.current_fastest_evaluation

        firing_rule = rule_selector.get_firing_rule_from_state(store.state)

        if not rule_is_large_wt(firing_rule):
            return RATING.NOT_APPLICABLE, None

        # TODO: We might want change the less than as well
        if firing_rule.comparison not in [
            COMPARATOR.GREATER_THEN,
            COMPARATOR.GREATER_THEN_OR_EQUAL,
        ]:
            return RATING.NOT_APPLICABLE, None

        base_max_waiting_time = base_evaluation.get_max_waiting_time_of_task_id(
            rule_selector.batching_rule_task_id, store
        )

        # If the max waiting time is very close to the firing rule value, that means
        # that the rule is actually "doing" something, meaning we might want to consider decreasing it
        if base_max_waiting_time < (firing_rule.value * (1 - CLOSENESS_TO_MAX_WT)):
            return RATING.NOT_APPLICABLE, None

        constraints = store.constraints.get_batching_large_wt_rule_constraints(
            rule_selector.batching_rule_task_id
        )

        max_allowed_min_size = max(
            [constraint.min_wt for constraint in constraints], default=0
        )

        # Decrementing the size would break the constraints
        if (firing_rule.value - SIZE_OF_CHANGE) < max_allowed_min_size:
            return RATING.NOT_APPLICABLE, None

        return (
            RATING.MEDIUM,
            ModifyLargeWtRuleAction(
                ModifyLargeWtRuleActionParamsType(
                    wt_increment=-1 * SIZE_OF_CHANGE,
                    rule=rule_selector,
                )
            ),
        )
