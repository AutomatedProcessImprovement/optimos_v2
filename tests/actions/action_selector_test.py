from dataclasses import replace
from o2.store import Store
from o2.actions.action_selector import ActionSelector
from optimos_v2.tests.fixtures.timetable_generator import TimetableGenerator


def test_only_one_rule(store: Store):
    store.replaceTimetable(batch_processing=[store.state.timetable.batch_processing[0]])
    bestAction = ActionSelector.find_most_impactful_batching_rule(store)
    assert bestAction is not None
    assert bestAction.id() == store.state.timetable.batch_processing[0].id()


def test_two_rules_one_bigger(store: Store):
    small_rule = TimetableGenerator.batching_size_rule(
        TimetableGenerator.FIRST_ACTIVITY, 1
    )
    big_rule = TimetableGenerator.batching_size_rule(
        TimetableGenerator.LAST_ACTIVITY, 50
    )
    store.replaceTimetable(batch_processing=[small_rule, big_rule])
    bestAction = ActionSelector.find_most_impactful_batching_rule(store)
    assert bestAction is not None
    assert big_rule.id() == bestAction.id()

    store.replaceTimetable(batch_processing=[big_rule, small_rule])
    bestActionRev = ActionSelector.find_most_impactful_batching_rule(store)

    assert bestActionRev is not None
    assert big_rule.id() == bestActionRev.id()
