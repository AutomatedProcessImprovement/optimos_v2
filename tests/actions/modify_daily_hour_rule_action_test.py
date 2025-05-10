from o2.actions.batching_actions.modify_daily_hour_rule_action import (
    ModifyDailyHourRuleAction,
    ModifyDailyHourRuleActionParamsType,
)
from o2.models.rule_selector import RuleSelector
from o2.models.self_rating import RATING
from o2.store import Store
from tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.test_helpers import (
    first_valid,
    replace_constraints,
    replace_timetable,
)
from tests.fixtures.timetable_generator import TimetableGenerator


def test_add_to_greater_then(store: Store):
    store = replace_timetable(
        store,
        batch_processing=[TimetableGenerator.daily_hour_rule(TimetableGenerator.FIRST_ACTIVITY, 9, 12)],
    )
    first_rule = store.base_timetable.batch_processing[0]
    greater_then_selector = RuleSelector.from_batching_rule(first_rule, (0, 0))

    action = ModifyDailyHourRuleAction(
        ModifyDailyHourRuleActionParamsType(rule=greater_then_selector, hour_increment=1)
    )

    new_state = action.apply(state=store.base_state)
    assert first_rule.task_id == new_state.timetable.batch_processing[0].task_id
    assert new_state.timetable.batch_processing[0].firing_rules[0][0].value == 10
    assert len(new_state.timetable.batch_processing[0].firing_rules[0]) == 3


def test_add_to_less_then(store: Store):
    store = replace_timetable(
        store,
        batch_processing=[TimetableGenerator.daily_hour_rule(TimetableGenerator.FIRST_ACTIVITY, 9, 12)],
    )
    first_rule = store.base_timetable.batch_processing[0]
    less_then_selector = RuleSelector.from_batching_rule(first_rule, (0, 1))

    action = ModifyDailyHourRuleAction(
        ModifyDailyHourRuleActionParamsType(rule=less_then_selector, hour_increment=-1)
    )

    new_state = action.apply(state=store.base_state)
    assert first_rule.task_id == new_state.timetable.batch_processing[0].task_id
    assert new_state.timetable.batch_processing[0].firing_rules[0][1].value == 11
    assert len(new_state.timetable.batch_processing[0].firing_rules[0]) == 3


def test_self_rate_simple(one_task_store: Store):
    # TODO: Fix this test, see implementation comments
    store = replace_timetable(
        one_task_store,
        batch_processing=[TimetableGenerator.daily_hour_rule(TimetableGenerator.FIRST_ACTIVITY, 9, 12)],
        task_resource_distribution=TimetableGenerator(one_task_store.base_state.bpmn_definition)
        # 1 Minute Tasks
        .create_simple_task_resource_distribution(60)
        .timetable.task_resource_distribution,
    )

    store = replace_constraints(
        store,
        batching_constraints=ConstraintsGenerator(store.base_state.bpmn_definition)
        .add_daily_hour_constraint()
        .constraints.batching_constraints,
    )

    first_rule = store.base_timetable.batch_processing[0]

    # Use solution directly for the test
    rating, action = first_valid(store, ModifyDailyHourRuleAction.rate_self(store, store.solution))

    # It's easy to see why the second rule is more impactful: If we remove <= 12:00,
    # than we can work from 9:00-23:59 (which is even more than needed, because we only
    # generate a 100 events), if we're removing >= 09:00, we can only work
    # from 00:00 - 12:00, which means that with 100 Events * avg. 10 minutes per event
    # = 1000 minutes = 16.6h, that we'll need more than 1 day to finish the work.
    assert rating == RATING.MEDIUM
    assert action == ModifyDailyHourRuleAction(
        ModifyDailyHourRuleActionParamsType(
            rule=RuleSelector.from_batching_rule(first_rule, (0, 1)), hour_increment=1
        )
    )


def test_self_rate_simple2(one_task_store: Store):
    # TODO: Fix this test, see implementation comments
    """
    Tests for the greater then rule, being detected as the most
    impactful (most increasing ) one
    """

    store = replace_timetable(
        one_task_store,
        batch_processing=[TimetableGenerator.daily_hour_rule(TimetableGenerator.FIRST_ACTIVITY, 9, 12)],
        arrival_time_calendar=TimetableGenerator(one_task_store.base_state.bpmn_definition)
        # Events come in from 10:00-17:00
        .create_simple_arrival_time_calendar(00, 12)
        .timetable.arrival_time_calendar,
        task_resource_distribution=TimetableGenerator(one_task_store.base_state.bpmn_definition)
        # 1 Minute Tasks
        .create_simple_task_resource_distribution(60)
        .timetable.task_resource_distribution,
    )

    store = replace_constraints(
        store,
        batching_constraints=ConstraintsGenerator(store.base_state.bpmn_definition)
        .add_daily_hour_constraint()
        .constraints.batching_constraints,
    )

    first_rule = store.base_timetable.batch_processing[0]

    # Use solution directly for the test
    rating, action = first_valid(store, ModifyDailyHourRuleAction.rate_self(store, store.solution))

    # Because events are coming only until 12:00, we can't work significantly
    # past that time. Therefore the first rule is more impactful.
    assert rating == RATING.MEDIUM
    assert action == ModifyDailyHourRuleAction(
        ModifyDailyHourRuleActionParamsType(
            rule=RuleSelector.from_batching_rule(first_rule, (0, 0)), hour_increment=-1
        )
    )
