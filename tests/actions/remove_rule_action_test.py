from o2.actions.action_selector import ActionSelector
from o2.actions.remove_rule_action import (
    RemoveRuleAction,
    RemoveRuleActionParamsType,
)
from o2.models.constraints import BATCH_TYPE, RULE_TYPE
from o2.models.rule_selector import RuleSelector
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.timetable import COMPARATOR, BatchingRule, FiringRule
from o2.store import Store
from tests.fixtures.timetable_generator import TimetableGenerator


def test_remove_single_rule(store: Store):
    store.replaceTimetable(
        batch_processing=[
            TimetableGenerator.batching_size_rule(TimetableGenerator.FIRST_ACTIVITY, 2)
        ]
    )
    first_rule = store.base_solution.timetable.batch_processing[0]
    selector = RuleSelector.from_batching_rule(first_rule, (0, 0))
    action = RemoveRuleAction(RemoveRuleActionParamsType(rule=selector))
    new_state = action.apply(state=store.base_solution)
    assert len(new_state.timetable.batch_processing) == 0


def test_remove_one_of_two_batching_rules(store: Store):
    store.replaceTimetable(
        batch_processing=[
            TimetableGenerator.batching_size_rule(TimetableGenerator.FIRST_ACTIVITY, 2),
            TimetableGenerator.batching_size_rule(
                TimetableGenerator.SECOND_ACTIVITY, 2
            ),
        ]
    )
    first_rule = store.base_solution.timetable.batch_processing[0]
    selector = RuleSelector.from_batching_rule(first_rule, (0, 0))
    action = RemoveRuleAction(RemoveRuleActionParamsType(rule=selector))
    new_state = action.apply(state=store.base_solution)
    assert len(new_state.timetable.batch_processing) == 1
    assert new_state.timetable.batch_processing[0].task_id == "SECOND_ACTIVITY"


def test_remove_one_of_two_firing_rules(store: Store):
    batching_rule = TimetableGenerator.batching_size_rule(
        TimetableGenerator.FIRST_ACTIVITY, 2
    )
    batching_rule.firing_rules.append(
        [
            FiringRule(
                attribute=RULE_TYPE.SIZE,
                comparison=COMPARATOR.EQUAL,
                value=42,
            )
        ]
    )
    store.replaceTimetable(batch_processing=[batching_rule])
    first_rule = store.base_solution.timetable.batch_processing[0]
    selector = RuleSelector.from_batching_rule(first_rule, (0, 0))
    action = RemoveRuleAction(RemoveRuleActionParamsType(rule=selector))
    new_state = action.apply(state=store.base_solution)
    assert len(new_state.timetable.batch_processing[0].firing_rules) == 1
    assert new_state.timetable.batch_processing[0].firing_rules[0][0].value == 42


def test_remove_complex_firing_rule(store: Store):
    batching_rule = BatchingRule(
        task_id=TimetableGenerator.SECOND_ACTIVITY,
        type=BATCH_TYPE.PARALLEL,
        size_distrib=[],
        duration_distrib=[],
        firing_rules=[
            [
                FiringRule(
                    attribute=RULE_TYPE.SIZE,
                    comparison=COMPARATOR.EQUAL,
                    value=41,
                ),
            ],
            [
                FiringRule(
                    attribute=RULE_TYPE.SIZE,
                    comparison=COMPARATOR.EQUAL,
                    value=41,
                ),
                FiringRule(
                    attribute=RULE_TYPE.SIZE,
                    comparison=COMPARATOR.EQUAL,
                    value=42,
                ),
                FiringRule(
                    attribute=RULE_TYPE.SIZE,
                    comparison=COMPARATOR.EQUAL,
                    value=43,
                ),
            ],
            [
                FiringRule(
                    attribute=RULE_TYPE.SIZE,
                    comparison=COMPARATOR.EQUAL,
                    value=44,
                ),
            ],
        ],
    )
    store.base_solution.timetable.batch_processing.insert(1, batching_rule)

    second_rule = store.base_solution.timetable.batch_processing[1]
    selector = RuleSelector.from_batching_rule(second_rule, (1, 1))
    action = RemoveRuleAction(RemoveRuleActionParamsType(rule=selector))
    new_state = action.apply(state=store.base_solution)
    assert len(new_state.timetable.batch_processing[1].firing_rules[1]) == 2
    assert new_state.timetable.batch_processing[1].firing_rules[1][0].value == 41
    assert new_state.timetable.batch_processing[1].firing_rules[1][1].value == 43
    assert new_state.timetable.batch_processing[1].firing_rules[0][0].value == 41
    assert new_state.timetable.batch_processing[1].firing_rules[2][0].value == 44


def test_self_rating_optimal_rule(store: Store):
    store.replaceTimetable(
        batch_processing=[
            TimetableGenerator.batching_size_rule(
                TimetableGenerator.FIRST_ACTIVITY, 3, 0.1
            )
        ]
    )

    store.evaluate()
    evaluations = ActionSelector.evaluate_rules(store)
    rating_input = SelfRatingInput.from_rule_solutions(store, evaluations)
    assert rating_input is not None
    result = next(RemoveRuleAction.rate_self(store, rating_input), None)
    assert result is None


def test_self_rating_non_optimal_rule(one_task_store: Store):
    store = one_task_store
    store.replaceTimetable(
        batch_processing=[
            TimetableGenerator.batching_size_rule(
                TimetableGenerator.FIRST_ACTIVITY, 50, 1
            )
        ],
        task_resource_distribution=TimetableGenerator(
            store.base_solution.bpmn_definition
        )
        # 1 Minute Tasks
        .create_simple_task_resource_distribution(60)
        # TODO: Improve Syntax
        .timetable.task_resource_distribution,
    )
    store.evaluate()
    evaluations = ActionSelector.evaluate_rules(store)
    rating_input = SelfRatingInput.from_rule_solutions(store, evaluations)
    assert rating_input is not None
    result = next(RemoveRuleAction.rate_self(store, rating_input))
    assert result[0] == RATING.LOW
    assert result[1] is not None
