from o2.store import Store
from o2.types.rule_selector import RuleSelector
from o2.actions.add_week_day_rule_action import (
    AddWeekDayRuleAction,
    AddWeekDayRuleActionParamsType,
)
from o2.types.days import DAY
from o2.actions.action_selector import ActionSelector
from o2.actions.modify_large_wt_rule_action import ModifyLargeWtRuleAction
from o2.types.self_rating import RATING, SelfRatingInput
from optimos_v2.tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.timetable_generator import TimetableGenerator


def test_add_day_simple(store: Store):
    store.replaceTimetable(
        batch_processing=[
            TimetableGenerator.week_day_rule(
                TimetableGenerator.FIRST_ACTIVITY, DAY.MONDAY, include_monday=False
            )
        ]
    )
    first_rule = store.state.timetable.batch_processing[0]

    selector = RuleSelector.from_batching_rule(first_rule, (0, 0))
    action = AddWeekDayRuleAction(
        AddWeekDayRuleActionParamsType(rule=selector, add_days=[DAY.TUESDAY])
    )
    new_state = action.apply(state=store.state)
    assert first_rule.task_id == new_state.timetable.batch_processing[0].task_id
    assert (
        new_state.timetable.batch_processing[0].firing_rules[0][0].value == DAY.MONDAY
    )
    assert len(new_state.timetable.batch_processing[0].firing_rules[0]) == 2
    assert (
        new_state.timetable.batch_processing[0].firing_rules[1][0].value == DAY.TUESDAY
    )
    assert len(new_state.timetable.batch_processing[0].firing_rules[1]) == 2


def test_self_rate_simple(one_task_store: Store):
    store = one_task_store
    store.replaceTimetable(
        batch_processing=[
            TimetableGenerator.week_day_rule(
                TimetableGenerator.FIRST_ACTIVITY, DAY.WEDNESDAY
            )
        ],
        task_resource_distribution=TimetableGenerator(store.state.bpmn_definition)
        # 12 Hour Tasks
        .create_simple_task_resource_distribution(4 * 60 * 60)
        # TODO: Improve Syntax
        .timetable.task_resource_distribution,
    )

    store.replaceConstraints(
        batching_constraints=ConstraintsGenerator(store.state.bpmn_definition)
        .add_week_day_constraint()
        .constraints.batching_constraints
    )
    store.evaluate()
    evaluations = ActionSelector.evaluate_rules(store)
    rating_input = SelfRatingInput(
        evaluations,
        RuleSelector(
            batching_rule_task_id=TimetableGenerator.FIRST_ACTIVITY,
            firing_rule_index=(1, 0),
        ),
    )
    assert rating_input is not None
    result = AddWeekDayRuleAction.rate_self(store, rating_input)
    assert result[0] == RATING.MEDIUM
    assert result[1] is not None
