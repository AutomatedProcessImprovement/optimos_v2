from o2.actions.action_selector import ActionSelector
from o2.actions.add_week_day_rule_action import (
    AddWeekDayRuleAction,
    AddWeekDayRuleActionParamsType,
)
from o2.actions.modify_large_wt_rule_action import ModifyLargeWtRuleAction
from o2.models.days import DAY
from o2.models.rule_selector import RuleSelector
from o2.models.self_rating import RATING, SelfRatingInput
from o2.store import Store
from tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.test_helpers import replace_constraints, replace_timetable
from tests.fixtures.timetable_generator import TimetableGenerator


def test_add_day_simple(store: Store):
    store = replace_timetable(
        store,
        batch_processing=[
            TimetableGenerator.week_day_rule(
                TimetableGenerator.FIRST_ACTIVITY, DAY.MONDAY, include_monday=False
            )
        ],
    )
    first_rule = store.base_timetable.batch_processing[0]

    selector = RuleSelector.from_batching_rule(first_rule, (0, 0))
    action = AddWeekDayRuleAction(
        AddWeekDayRuleActionParamsType(rule=selector, add_days=[DAY.TUESDAY])
    )
    new_state = action.apply(state=store.base_state)
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
    store = replace_timetable(
        one_task_store,
        batch_processing=[
            TimetableGenerator.week_day_rule(
                TimetableGenerator.FIRST_ACTIVITY, DAY.WEDNESDAY
            )
        ],
        # 4 Hour Tasks
        task_resource_distribution=TimetableGenerator.simple_task_resource_distribution(
            [TimetableGenerator.FIRST_ACTIVITY], 4 * 60 * 60
        ),
    )

    store = replace_constraints(
        store,
        batching_constraints=[
            ConstraintsGenerator.week_day_constraint(
                [TimetableGenerator.FIRST_ACTIVITY]
            )
        ],
    )
    evaluations = ActionSelector.evaluate_rules(store)
    rating_input = SelfRatingInput(
        store.solution,
        evaluations,
        RuleSelector(
            batching_rule_task_id=TimetableGenerator.FIRST_ACTIVITY,
            firing_rule_index=(1, 0),
        ),
    )
    assert rating_input is not None
    rating, action = next(AddWeekDayRuleAction.rate_self(store, rating_input))
    assert rating == RATING.MEDIUM
    assert action is not None
