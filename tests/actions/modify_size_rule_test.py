from dataclasses import replace

import pandas as pd
from o2.store import Store
from o2.actions.action_selector import ActionSelector
from o2.actions.modify_size_rule_action import (
    ModifySizeRuleAction,
    ModifySizeRuleActionParamsType,
)
from o2.types.constraints import RULE_TYPE
from o2.types.rule_selector import RuleSelector
from o2.types.timetable import COMPARATOR, BatchingRule, FiringRule
from o2.types.self_rating import RATING, SelfRatingInput
from optimos_v2.tests.fixtures.constraints_generator import ConstraintsGenerator
from optimos_v2.tests.fixtures.timetable_generator import TimetableGenerator


def test_increment_size(store: Store):
    new_size = TimetableGenerator.BATCHING_BASE_SIZE + 1
    first_rule = store.state.timetable.batch_processing[0]

    selector = RuleSelector.from_batching_rule(first_rule, (0, 0))
    action = ModifySizeRuleAction(
        ModifySizeRuleActionParamsType(
            rule=selector, size_increment=1, duration_fn="0.8*size"
        )
    )
    new_state = action.apply(state=store.state)
    assert first_rule.task_id == new_state.timetable.batch_processing[0].task_id
    assert helper_rule_matches_size(new_state.timetable.batch_processing[0], new_size)


def test_decrement_size(store: Store):
    new_size = TimetableGenerator.BATCHING_BASE_SIZE - 1
    first_rule = store.state.timetable.batch_processing[0]
    selector = RuleSelector.from_batching_rule(first_rule, (0, 0))
    action = ModifySizeRuleAction(
        ModifySizeRuleActionParamsType(
            rule=selector, size_increment=-1, duration_fn="0.8*size"
        )
    )
    new_state = action.apply(state=store.state)
    assert first_rule.task_id == new_state.timetable.batch_processing[0].task_id
    assert helper_rule_matches_size(new_state.timetable.batch_processing[0], new_size)


def test_self_rating_optimal_rule(store: Store):
    store.replaceTimetable(
        batch_processing=[
            TimetableGenerator.batching_size_rule(TimetableGenerator.FIRST_ACTIVITY, 2)
        ]
    )

    store.replaceConstraints(
        batching_constraints=ConstraintsGenerator(store.state.bpmn_definition)
        .add_size_constraint(2)
        .constraints.batching_constraints
    )
    store.evaluate()
    evaluations = ActionSelector.evaluate_rules(store)
    rating_input = SelfRatingInput.from_rule_evaluations(evaluations)
    assert rating_input is not None
    result = ModifySizeRuleAction.rate_self(store, rating_input)
    assert result == (0, None)


def test_self_rating_non_optimal_rule(store: Store):
    store.replaceTimetable(
        batch_processing=[
            TimetableGenerator.batching_size_rule(TimetableGenerator.FIRST_ACTIVITY, 10)
        ]
    )
    store.replaceConstraints(
        batching_constraints=ConstraintsGenerator(store.state.bpmn_definition)
        .add_size_constraint(5)
        .constraints.batching_constraints
    )
    store.evaluate()
    evaluations = ActionSelector.evaluate_rules(store)
    rating_input = SelfRatingInput.from_rule_evaluations(evaluations)
    assert rating_input is not None
    result = ModifySizeRuleAction.rate_self(store, rating_input)
    assert result[0] == RATING.MEDIUM
    assert result[1] is not None


def helper_rule_matches_size(rule: BatchingRule, size: int):
    assert len(rule.firing_rules) == 1
    assert len(rule.firing_rules[0]) == 1
    assert rule.firing_rules[0][0] == FiringRule(
        attribute=RULE_TYPE.SIZE, comparison=COMPARATOR.EQUAL, value=size
    )
    assert len(rule.size_distrib) == 2
    # Check for first distribution rule (that forbids execution without batching)
    assert rule.size_distrib[0].key == "1"
    assert rule.size_distrib[0].value == 0
    # Check for actual distribution rule
    assert rule.size_distrib[1].key == str(size)
    return True
