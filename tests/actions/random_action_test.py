from unittest import mock

import pytest

from o2.actions.base_actions.add_datetime_rule_base_action import AddDateTimeRuleAction
from o2.actions.base_actions.add_ready_large_wt_rule_base_action import AddReadyLargeWTRuleAction
from o2.actions.base_actions.add_size_rule_base_action import AddSizeRuleAction
from o2.actions.base_actions.modify_size_rule_base_action import ModifySizeRuleAction
from o2.actions.batching_actions.modify_daily_hour_rule_action import ModifyDailyHourRuleAction
from o2.actions.batching_actions.random_action import (
    RandomAction,
)
from o2.actions.batching_actions.remove_rule_action import RemoveRuleAction
from o2.models.days import DAY
from o2.models.rule_selector import RuleSelector
from o2.models.settings import Settings
from o2.models.solution import Solution
from o2.models.timetable import RULE_TYPE, BatchingRule
from o2.store import Store
from tests.fixtures.test_helpers import replace_timetable
from tests.fixtures.timetable_generator import TimetableGenerator


@pytest.fixture
def self_rating_input():
    # Create a mock for Solution that properly handles timetable access
    mock_solution = mock.MagicMock(spec=Solution)

    # Create a mock state and timetable that will be used by all tests
    mock_timetable = mock.MagicMock()
    mock_timetable.get_task_ids.return_value = [TimetableGenerator.FIRST_ACTIVITY]

    # Create a mock state with the mock timetable
    mock_state = mock.MagicMock()
    mock_state.timetable = mock_timetable

    # Set up the solution's state and timetable property access
    mock_solution.state = mock_state
    # Mock the timetable property to return the state's timetable
    type(mock_solution).timetable = mock.PropertyMock(return_value=mock_timetable)

    return mock_solution


@pytest.fixture
def mock_rule():
    """Creates a mock BatchingRule with a rule selector."""
    rule = mock.MagicMock(spec=BatchingRule)
    rule.task_id = TimetableGenerator.FIRST_ACTIVITY

    # Create a mock rule selector
    rule_selector = mock.MagicMock(spec=RuleSelector)
    rule_selector.batching_rule_task_id = TimetableGenerator.FIRST_ACTIVITY
    rule.get_firing_rule_selectors.return_value = [rule_selector]

    return rule, rule_selector


def get_next_action(store, self_rating_input, mock_choice_vals, mock_randint_vals=None):
    """Helper function to get the next action from RandomAction.rate_self with mocked random values."""
    with mock.patch("random.choice") as mock_choice:
        mock_choice.side_effect = mock_choice_vals

        if mock_randint_vals:
            with mock.patch("random.randint") as mock_randint:
                mock_randint.side_effect = mock_randint_vals
                generator = RandomAction.rate_self(store, self_rating_input)
                return next(generator)
        else:
            generator = RandomAction.rate_self(store, self_rating_input)
            return next(generator)


def test_rate_self_add_datetime_rule(store: Store, self_rating_input: Solution):
    """Test that RandomAction can generate an AddDateTimeRuleAction correctly."""
    mock_choice_vals = [
        AddDateTimeRuleAction,  # First choose the action type
        TimetableGenerator.FIRST_ACTIVITY,  # First choose a task_id
        DAY.MONDAY,  # Then choose a day
    ]
    mock_randint_vals = [8, 9]  # start_time, end_time

    rating, action = get_next_action(store, self_rating_input, mock_choice_vals, mock_randint_vals)

    # Verify it's the right type
    assert isinstance(action, AddDateTimeRuleAction)
    # Access TypedDict attributes with bracket notation
    assert action.params["task_id"] == TimetableGenerator.FIRST_ACTIVITY
    assert action.params["time_period"].from_ == DAY.MONDAY
    assert action.params["time_period"].begin_time == "08:00:00"
    assert action.params["time_period"].end_time == "09:00:00"


def test_rate_self_add_ready_large_wt_rule(store: Store, self_rating_input: Solution):
    """Test that RandomAction can generate an AddReadyLargeWTRuleAction correctly."""
    mock_choice_vals = [
        AddReadyLargeWTRuleAction,  # Action type
        TimetableGenerator.FIRST_ACTIVITY,  # Task ID
        RULE_TYPE.LARGE_WT,  # Rule type
    ]
    mock_randint_vals = [600]  # Waiting time (10 minutes)

    rating, action = get_next_action(store, self_rating_input, mock_choice_vals, mock_randint_vals)

    # Verify
    assert isinstance(action, AddReadyLargeWTRuleAction)
    assert action.params["task_id"] == TimetableGenerator.FIRST_ACTIVITY
    assert action.params["waiting_time"] == 600
    assert action.params["type"] == RULE_TYPE.LARGE_WT


def test_rate_self_add_size_rule(store: Store, self_rating_input: Solution):
    """Test that RandomAction can generate an AddSizeRuleAction correctly."""
    mock_choice_vals = [
        AddSizeRuleAction,  # Action type
        TimetableGenerator.FIRST_ACTIVITY,  # Task ID
    ]

    rating, action = get_next_action(store, self_rating_input, mock_choice_vals)

    # Verify
    assert isinstance(action, AddSizeRuleAction)
    assert action.params["task_id"] == TimetableGenerator.FIRST_ACTIVITY
    assert action.params["size"] == 2  # Default size in random_action.py


def test_rate_self_modify_daily_hour_rule(store: Store, self_rating_input: Solution, mock_rule):
    """Test that RandomAction can generate a ModifyDailyHourRuleAction correctly."""
    rule, rule_selector = mock_rule

    # Set up the rule to return the right selector based on rule type
    rule.get_firing_rule_selectors.side_effect = (
        lambda rule_type=None: [rule_selector]
        if rule_type is None or rule_type == RULE_TYPE.DAILY_HOUR
        else []
    )

    # Replace the timetable in the store
    store = replace_timetable(store, batch_processing=[rule])

    # Configure the mock timetable's batch_processing property
    # We need to configure the property access on the mock
    self_rating_input.timetable.batch_processing = [rule]  # type: ignore

    # Using patching in get_next_action helper
    with mock.patch("o2.actions.batching_actions.random_action.random.choice") as mock_choice:
        # Set specific return values for each call
        mock_choice.side_effect = [
            ModifyDailyHourRuleAction,  # First call selects action type
            1,  # Second call selects hour increment from [-1, 1]
            rule_selector,  # Third call selects rule selector
        ]

        # Get the generator and extract the first yield
        generator = RandomAction.rate_self(store, self_rating_input)
        rating, action = next(generator)

        # Verify the action
        assert isinstance(action, ModifyDailyHourRuleAction)
        assert action.params["rule"] == rule_selector
        assert action.params["hour_increment"] == 1


def test_rate_self_modify_size_rule(store: Store, self_rating_input: Solution, mock_rule):
    """Test that RandomAction can generate a ModifySizeRuleAction correctly."""
    rule, rule_selector = mock_rule

    # Set up the rule to return the right selector based on rule type
    rule.get_firing_rule_selectors.side_effect = (
        lambda rule_type=None: [rule_selector] if rule_type is None or rule_type == RULE_TYPE.SIZE else []
    )

    # Replace the timetable in the store
    store = replace_timetable(store, batch_processing=[rule])

    # Configure the mock timetable's batch_processing property
    # Linter warning is expected here, but the code works correctly
    self_rating_input.timetable.batch_processing = [rule]  # type: ignore

    # Using patching directly
    with mock.patch("o2.actions.batching_actions.random_action.random.choice") as mock_choice:
        # Set specific return values for each call
        mock_choice.side_effect = [
            ModifySizeRuleAction,  # First call selects action type
            rule_selector,  # Second call selects rule selector
            TimetableGenerator.FIRST_ACTIVITY,  # Third call selects task ID
            1,  # Fourth call selects size increment
        ]

        # Get the generator and extract the first yield
        generator = RandomAction.rate_self(store, self_rating_input)
        rating, action = next(generator)

        # Verify the action
        assert isinstance(action, ModifySizeRuleAction)
        assert action.params["rule"] == rule_selector
        assert action.params["size_increment"] == 1


@pytest.mark.parametrize(
    "disable_remove,expected_action_type",
    [
        (False, RemoveRuleAction),
        (True, AddSizeRuleAction),
    ],
)
def test_rate_self_remove_rule(
    store: Store, self_rating_input: Solution, mock_rule, disable_remove, expected_action_type
):
    """Test RemoveRuleAction with enabled/disabled settings."""
    rule, rule_selector = mock_rule

    # Set up the rule to return the right selector
    rule.get_firing_rule_selectors.return_value = [rule_selector]

    # Replace the timetable in the store
    store = replace_timetable(store, batch_processing=[rule])

    # Configure the mock timetable's batch_processing property
    # Linter warning is expected here, but the code works correctly
    self_rating_input.timetable.batch_processing = [rule]  # type: ignore

    # Set up the setting
    old_setting = Settings.DISABLE_REMOVE_ACTION_RULE
    Settings.DISABLE_REMOVE_ACTION_RULE = disable_remove

    try:
        # Using patching directly
        with mock.patch("o2.actions.batching_actions.random_action.random.choice") as mock_choice:
            if disable_remove:
                # When disabled, it skips RemoveRuleAction and uses AddSizeRuleAction
                mock_choice.side_effect = [
                    RemoveRuleAction,  # This should be skipped
                    AddSizeRuleAction,  # This should be chosen instead
                    TimetableGenerator.FIRST_ACTIVITY,  # Task ID
                ]
            else:
                mock_choice.side_effect = [
                    RemoveRuleAction,  # Action type
                    rule_selector,  # Rule selector
                ]

            # Get the generator and extract the first yield
            generator = RandomAction.rate_self(store, self_rating_input)
            rating, action = next(generator)

            # Verify the action
            assert isinstance(action, expected_action_type)
            if expected_action_type == RemoveRuleAction:
                assert action.params["rule"] == rule_selector
    finally:
        # Restore the setting
        Settings.DISABLE_REMOVE_ACTION_RULE = old_setting


def test_rate_self_skip_action_with_no_rules(store: Store, self_rating_input: Solution):
    """Test that RandomAction skips actions that require rules when none exist."""
    # Create an empty timetable with no rules
    store = replace_timetable(store, batch_processing=[])

    mock_choice_vals = [
        ModifySizeRuleAction,  # This should be skipped (no size rules)
        ModifyDailyHourRuleAction,  # This should be skipped (no hour rules)
        RemoveRuleAction,  # This should be skipped (no rules)
        AddSizeRuleAction,  # This should work
        TimetableGenerator.FIRST_ACTIVITY,  # Task ID
    ]

    rating, action = get_next_action(store, self_rating_input, mock_choice_vals)

    # Verify we got the action that doesn't need rules
    assert isinstance(action, AddSizeRuleAction)


def test_rate_self_unknown_action(store: Store, self_rating_input: Solution):
    """Test that RandomAction raises ValueError for unknown action types."""

    # Define a custom action class not in ACTIONS
    class UnknownAction:
        pass

    mock_choice_vals = [UnknownAction]

    with pytest.raises(ValueError, match="Unknown action"):
        get_next_action(store, self_rating_input, mock_choice_vals)
