from unittest.mock import MagicMock

import pytest

from o2.actions.base_actions.add_datetime_rule_base_action import AddDateTimeRuleAction
from o2.actions.base_actions.add_ready_large_wt_rule_base_action import AddReadyLargeWTRuleAction
from o2.actions.base_actions.modify_size_rule_base_action import ModifySizeRuleAction
from o2.actions.base_actions.shift_datetime_rule_base_action import ShiftDateTimeRuleAction
from o2.actions.batching_actions.modify_large_ready_wt_of_significant_rule_action import (
    ModifyLargeReadyWtOfSignificantRuleAction,
)
from o2.actions.batching_actions.modify_size_of_significant_rule_action import (
    ModifySizeOfSignificantRuleAction,
)
from o2.actions.batching_actions.remove_date_time_rule_action import RemoveDateTimeRuleAction
from o2.models.solution import Solution


@pytest.fixture
def mock_store_and_solution():
    """Create mock store and solution objects for testing."""
    mock_store = MagicMock()
    mock_solution = MagicMock(spec=Solution)
    return mock_store, mock_solution


def test_modify_size_of_significant_rule_action_rate_self(mock_store_and_solution):
    """Test that ModifySizeOfSignificantRuleAction.rate_self throws NotImplementedError."""
    mock_store, mock_solution = mock_store_and_solution
    with pytest.raises(NotImplementedError):
        next(ModifySizeOfSignificantRuleAction.rate_self(mock_store, mock_solution))


def test_remove_date_time_rule_action_rate_self(mock_store_and_solution):
    """Test that RemoveDateTimeRuleAction.rate_self throws NotImplementedError."""
    mock_store, mock_solution = mock_store_and_solution
    with pytest.raises(NotImplementedError):
        next(RemoveDateTimeRuleAction.rate_self(mock_store, mock_solution))


def test_modify_large_ready_wt_of_significant_rule_action_rate_self(mock_store_and_solution):
    """Test that ModifyLargeReadyWtOfSignificantRuleAction.rate_self throws NotImplementedError."""
    mock_store, mock_solution = mock_store_and_solution
    with pytest.raises(NotImplementedError):
        next(ModifyLargeReadyWtOfSignificantRuleAction.rate_self(mock_store, mock_solution))


def test_modify_size_rule_action_rate_self(mock_store_and_solution):
    """Test that ModifySizeRuleAction.rate_self throws NotImplementedError."""
    mock_store, mock_solution = mock_store_and_solution
    with pytest.raises(NotImplementedError):
        next(ModifySizeRuleAction.rate_self(mock_store, mock_solution))


def test_shift_datetime_rule_action_rate_self(mock_store_and_solution):
    """Test that ShiftDateTimeRuleAction.rate_self throws NotImplementedError."""
    mock_store, mock_solution = mock_store_and_solution
    with pytest.raises(NotImplementedError):
        next(ShiftDateTimeRuleAction.rate_self(mock_store, mock_solution))


def test_add_datetime_rule_action_rate_self(mock_store_and_solution):
    """Test that AddDateTimeRuleAction.rate_self throws NotImplementedError."""
    mock_store, mock_solution = mock_store_and_solution
    with pytest.raises(NotImplementedError):
        next(AddDateTimeRuleAction.rate_self(mock_store, mock_solution))


def test_add_ready_large_wt_rule_action_rate_self(mock_store_and_solution):
    """Test that AddReadyLargeWTRuleAction.rate_self throws NotImplementedError."""
    mock_store, mock_solution = mock_store_and_solution
    with pytest.raises(NotImplementedError):
        next(AddReadyLargeWTRuleAction.rate_self(mock_store, mock_solution))
