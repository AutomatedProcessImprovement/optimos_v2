from o2.actions.base_action import BaseAction, BaseActionParamsType
from o2.types.state import State
from o2.store import Store
from o2.types.self_rating import RATING, SelfRatingInput


class RemoveRuleActionParamsType(BaseActionParamsType):
    pass


class RemoveRuleAction(BaseAction):
    params: RemoveRuleActionParamsType

    # Returns a copy of the timetable with the rule removed
    # (TimetableType is a frozen dataclass)
    def apply(self, state: State, enable_prints=True):
        timetable = state.timetable
        rule_selector = self.params["rule"]

        index, rule = next(
            (
                (i, rule)
                for i, rule in enumerate(timetable.batch_processing)
                if rule_selector.batching_rule_task_id == rule.task_id
            ),
            [None, None],
        )
        if rule is None or index is None:
            print(f"BatchingRule not found for {rule_selector}")
            return state
        if enable_prints:
            print(f"\t\t>> Removing rule {rule_selector}")

        new_batching_rule = rule.remove_firing_rule(rule_selector)
        if new_batching_rule is None:
            return state.replaceTimetable(
                batch_processing=timetable.batch_processing[:index]
                + timetable.batch_processing[index + 1 :],
            )

        return state.replaceTimetable(
            batch_processing=timetable.batch_processing[:index]
            + [new_batching_rule]
            + timetable.batch_processing[index + 1 :],
        )

    @staticmethod
    def rate_self(store: Store, input: SelfRatingInput):
        rule_selector = input.most_impactful_rule
        evaluation = input.most_impactful_rule_evaluation
        # TODO: Check constraints
        # Check if this evaluation beats the current pareto front
        if store.current_pareto_front.is_dominated_by(evaluation):
            print(
                f"\t\t>> Most impactful rule dominates current. Rule: {rule_selector}"
            )
            return (
                RATING.EXTREME,
                RemoveRuleAction(RemoveRuleActionParamsType(rule=rule_selector)),
            )
        return RATING.NOT_APPLICABLE, None
