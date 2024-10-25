from o2.agents.tabu_agent import TabuAgent
from o2.actions.modify_large_wt_rule_action import (
    ModifyLargeWtRuleAction,
    ModifyLargeWtRuleActionParamsType,
)
from o2.models.rule_selector import RuleSelector
from o2.models.self_rating import RATING, SelfRatingInput
from o2.store import Store
from tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.test_helpers import (
    first_valid,
    assert_no_first_valid,
    replace_constraints,
    replace_timetable,
)
from tests.fixtures.timetable_generator import TimetableGenerator


def test_increment_size(store: Store):
    store = replace_timetable(
        store,
        batch_processing=[
            TimetableGenerator.large_wt_rule(TimetableGenerator.FIRST_ACTIVITY, 5 * 60)
        ],
    )
    first_rule = store.base_timetable.batch_processing[0]

    selector = RuleSelector.from_batching_rule(first_rule, (0, 1))
    action = ModifyLargeWtRuleAction(
        ModifyLargeWtRuleActionParamsType(rule=selector, wt_increment=1 * 60)
    )
    new_state = action.apply(state=store.base_state)
    assert first_rule.task_id == new_state.timetable.batch_processing[0].task_id
    assert new_state.timetable.batch_processing[0].firing_rules[0][1].value == (6 * 60)


def test_decrement_size(store: Store):
    store = replace_timetable(
        store,
        batch_processing=[
            TimetableGenerator.large_wt_rule(TimetableGenerator.FIRST_ACTIVITY, 5 * 60)
        ],
    )
    first_rule = store.base_timetable.batch_processing[0]

    selector = RuleSelector.from_batching_rule(first_rule, (0, 1))
    action = ModifyLargeWtRuleAction(
        ModifyLargeWtRuleActionParamsType(rule=selector, wt_increment=-1 * 60)
    )
    new_state = action.apply(state=store.base_state)
    assert first_rule.task_id == new_state.timetable.batch_processing[0].task_id
    assert new_state.timetable.batch_processing[0].firing_rules[0][1].value == (4 * 60)


def test_self_rating_optimal(one_task_store: Store):
    store = replace_timetable(
        one_task_store,
        batch_processing=[
            TimetableGenerator.large_wt_rule(
                TimetableGenerator.FIRST_ACTIVITY, 30 * 60, size=2
            )
        ],
        task_resource_distribution=TimetableGenerator(
            one_task_store.base_state.bpmn_definition
        )
        # 1 Minute Tasks
        .create_simple_task_resource_distribution(60)
        .timetable.task_resource_distribution,
    )

    store = replace_constraints(
        store,
        batching_constraints=ConstraintsGenerator(store.base_state.bpmn_definition)
        .add_large_wt_constraint()
        .constraints.batching_constraints,
    )

    evaluations = TabuAgent.evaluate_rules(store)
    rating_input = SelfRatingInput.from_rule_solutions(store, evaluations)
    assert rating_input is not None
    assert_no_first_valid(store, ModifyLargeWtRuleAction.rate_self(store, rating_input))


def test_self_rating_non_optimal(one_task_store: Store):
    store = replace_timetable(
        one_task_store,
        batch_processing=[
            TimetableGenerator.large_wt_rule(
                TimetableGenerator.FIRST_ACTIVITY, 30 * 60, size=10
            )
        ],
    )

    store = replace_constraints(
        store,
        batching_constraints=ConstraintsGenerator(store.base_state.bpmn_definition)
        .add_large_wt_constraint()
        .constraints.batching_constraints,
    )

    evaluations = TabuAgent.evaluate_rules(store)
    rating_input = SelfRatingInput(
        store.solution,
        evaluations,
        RuleSelector(TimetableGenerator.FIRST_ACTIVITY, (0, 1)),
    )
    assert rating_input is not None
    result = first_valid(store, ModifyLargeWtRuleAction.rate_self(store, rating_input))
    assert result[0] == RATING.MEDIUM
    assert result[1] is not None
