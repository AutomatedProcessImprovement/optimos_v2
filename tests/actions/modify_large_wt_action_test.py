from o2.store import Store
from o2.actions.action_selector import ActionSelector
from o2.types.rule_selector import RuleSelector
from o2.actions.modify_large_wt_action import (
    ModifyLargeWtRuleAction,
    ModifyLargeWtRuleActionParamsType,
)
from o2.types.self_rating import RATING, SelfRatingInput
from optimos_v2.tests.fixtures.constraints_generator import ConstraintsGenerator
from optimos_v2.tests.fixtures.timetable_generator import TimetableGenerator


def test_increment_size(store: Store):
    store.replaceTimetable(
        batch_processing=[
            TimetableGenerator.large_wt_rule(TimetableGenerator.FIRST_ACTIVITY, 5 * 60)
        ]
    )
    first_rule = store.state.timetable.batch_processing[0]

    selector = RuleSelector.from_batching_rule(first_rule, (0, 1))
    action = ModifyLargeWtRuleAction(
        ModifyLargeWtRuleActionParamsType(rule=selector, wt_increment=1 * 60)
    )
    new_state = action.apply(state=store.state)
    assert first_rule.task_id == new_state.timetable.batch_processing[0].task_id
    assert new_state.timetable.batch_processing[0].firing_rules[0][1].value == (6 * 60)


def test_decrement_size(store: Store):
    store.replaceTimetable(
        batch_processing=[
            TimetableGenerator.large_wt_rule(TimetableGenerator.FIRST_ACTIVITY, 5 * 60)
        ]
    )
    first_rule = store.state.timetable.batch_processing[0]

    selector = RuleSelector.from_batching_rule(first_rule, (0, 1))
    action = ModifyLargeWtRuleAction(
        ModifyLargeWtRuleActionParamsType(rule=selector, wt_increment=-1 * 60)
    )
    new_state = action.apply(state=store.state)
    assert first_rule.task_id == new_state.timetable.batch_processing[0].task_id
    assert new_state.timetable.batch_processing[0].firing_rules[0][1].value == (4 * 60)


def test_self_rating_optimal(one_task_store: Store):
    store = one_task_store
    store.replaceTimetable(
        batch_processing=[
            TimetableGenerator.large_wt_rule(
                TimetableGenerator.FIRST_ACTIVITY, 30 * 60, size=2
            )
        ]
    )

    store.replaceConstraints(
        batching_constraints=ConstraintsGenerator(store.state.bpmn_definition)
        .add_large_wt_constraint()
        .constraints.batching_constraints
    )
    store.evaluate()
    evaluations = ActionSelector.evaluate_rules(store)
    rating_input = SelfRatingInput.from_rule_evaluations(evaluations)
    assert rating_input is not None
    result = ModifyLargeWtRuleAction.rate_self(store, rating_input)
    assert result == (0, None)


def test_self_rating_non_optimal(one_task_store: Store):
    store = one_task_store
    store.replaceTimetable(
        batch_processing=[
            TimetableGenerator.large_wt_rule(
                TimetableGenerator.FIRST_ACTIVITY, 30 * 60, size=10
            )
        ]
    )

    store.replaceConstraints(
        batching_constraints=ConstraintsGenerator(store.state.bpmn_definition)
        .add_large_wt_constraint()
        .constraints.batching_constraints
    )
    store.evaluate()
    evaluations = ActionSelector.evaluate_rules(store)
    rating_input = SelfRatingInput(
        evaluations, RuleSelector(TimetableGenerator.FIRST_ACTIVITY, (0, 1))
    )
    assert rating_input is not None
    result = ModifyLargeWtRuleAction.rate_self(store, rating_input)
    assert result[0] == RATING.MEDIUM
    assert result[1] is not None
