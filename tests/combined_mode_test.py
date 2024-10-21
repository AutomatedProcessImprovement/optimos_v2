from o2.action_selectors.tabu_action_selector import TabuActionSelector
from o2.actions.modify_calendar_base_action import ModifyCalendarBaseAction
from o2.actions.modify_resource_base_action import ModifyResourceBaseAction
from o2.models.self_rating import RATING
from o2.models.settings import LegacyApproach
from o2.models.solution import Solution
from o2.store import SolutionTry, Store


def test_combined_mode(one_task_store: Store):
    store = one_task_store

    store.settings.legacy_approach = LegacyApproach.COMBINED
    store.settings.max_number_of_actions_to_select = 99

    # In the first step ModifyResource Actions are not allowed
    actions = TabuActionSelector.select_actions(store)
    assert actions is not None
    assert all(not isinstance(action, ModifyResourceBaseAction) for action in actions)

    # Apply a ModifyCalendar Action
    store.run_action(
        next(
            action for action in actions if isinstance(action, ModifyCalendarBaseAction)
        )
    )

    # In following step, ModifyResource Actions are allowed and
    # ModifyCalendar Actions are not allowed
    actions = TabuActionSelector.select_actions(store)
    assert actions is not None
    assert all(not isinstance(action, ModifyCalendarBaseAction) for action in actions)

    # And last but not least, we apply a ModifyResource Action
    store.run_action(
        next(
            action for action in actions if isinstance(action, ModifyResourceBaseAction)
        )
    )

    # In the next step, ModifyCalendar Actions are allowed again
    actions = TabuActionSelector.select_actions(store)
    assert actions is not None
    assert all(not isinstance(action, ModifyResourceBaseAction) for action in actions)


def test_multiple_actions_of_same_type(one_task_store: Store):
    # TODO : Think about this test

    store = one_task_store

    store.settings.legacy_approach = LegacyApproach.COMBINED
    store.settings.max_number_of_actions_to_select = 99

    # In the first step ModifyResource Actions are not allowed
    actions = TabuActionSelector.select_actions(store)
    assert actions is not None
    assert all(not isinstance(action, ModifyResourceBaseAction) for action in actions)

    assert len(actions) > 1

    # Apply a ModifyCalendar Action
    solutions = [
        Solution.from_parent(store.solution, action)
        for action in actions
        if isinstance(action, ModifyCalendarBaseAction)
    ]

    chosen, not_chosen = store.process_many_solutions(solutions)
    assert len(chosen) == 1
    assert len(not_chosen) > 1
    assert ModifyResourceBaseAction.get_default_rating(store) == RATING.HIGH
    assert ModifyCalendarBaseAction.get_default_rating(store) == RATING.LOW
