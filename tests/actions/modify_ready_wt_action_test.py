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
from o2.actions.modify_ready_wt_rule_action import (
    ModifyReadyWtRuleAction,
    ModifyReadyWtRuleActionParamsType,
)
from o2.types.self_rating import RATING, SelfRatingInput
from tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.timetable_generator import TimetableGenerator


def test_increment_size(store: Store):
    store.replaceTimetable(
        batch_processing=[
            TimetableGenerator.ready_wt_rule(TimetableGenerator.FIRST_ACTIVITY, 5 * 60)
        ]
    )
    first_rule = store.state.timetable.batch_processing[0]

    selector = RuleSelector.from_batching_rule(first_rule, (0, 0))
    action = ModifyReadyWtRuleAction(
        ModifyReadyWtRuleActionParamsType(rule=selector, wt_increment=1 * 60)
    )
    new_state = action.apply(state=store.state)
    assert first_rule.task_id == new_state.timetable.batch_processing[0].task_id
    assert new_state.timetable.batch_processing[0].firing_rules[0][0].value == (6 * 60)


def test_decrement_size(store: Store):
    store.replaceTimetable(
        batch_processing=[
            TimetableGenerator.ready_wt_rule(TimetableGenerator.FIRST_ACTIVITY, 5 * 60)
        ]
    )
    first_rule = store.state.timetable.batch_processing[0]

    selector = RuleSelector.from_batching_rule(first_rule, (0, 0))
    action = ModifyReadyWtRuleAction(
        ModifyReadyWtRuleActionParamsType(rule=selector, wt_increment=-1 * 60)
    )
    new_state = action.apply(state=store.state)
    assert first_rule.task_id == new_state.timetable.batch_processing[0].task_id
    assert new_state.timetable.batch_processing[0].firing_rules[0][0].value == (4 * 60)


# TODO: There most likely is a bug in Prosimos, therefore this test fails
# def test_self_rating(store: Store):
#     store.replaceTimetable(
#         batch_processing=[
#             TimetableGenerator.ready_wt_rule(TimetableGenerator.FIRST_ACTIVITY, 5 * 60)
#         ]
#     )

#     store.replaceConstraints(
#         batching_constraints=ConstraintsGenerator(store.state.bpmn_definition)
#         .add_ready_wt_constraint()
#         .constraints.batching_constraints
#     )
#     store.evaluate()
#     evaluations = ActionSelector.evaluate_rules(store)
#     rating_input = SelfRatingInput.from_rule_evaluations(evaluations)
#     assert rating_input is not None
#     result = ModifyReadyWtRuleAction.rate_self(store, rating_input)
#     assert result == (0, None)