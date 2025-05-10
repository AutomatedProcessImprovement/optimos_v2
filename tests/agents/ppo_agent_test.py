from unittest import mock

import numpy as np
import pytest
import torch as th

from o2.actions.base_actions.base_action import BaseAction
from o2.agents.agent import NoActionsLeftError
from o2.agents.ppo_agent import PPOAgent
from o2.agents.tabu_agent import TabuAgent
from o2.models.solution import Solution
from o2.pareto_front import FRONT_STATUS

# These fixtures are now available from conftest.py automatically
# No need to explicitly import them


@pytest.fixture
def mock_maskable_ppo():
    """Create a mock MaskablePPO model"""
    mockable_ppo = mock.MagicMock()
    mock_policy = mock.MagicMock()
    mockable_ppo.policy = mock_policy
    mockable_ppo._last_obs = {}
    mockable_ppo.device = "cpu"
    mockable_ppo.rollout_buffer = mock.MagicMock()
    return mockable_ppo


@pytest.fixture
def mock_env():
    """Create a mock gym environment"""
    env = mock.MagicMock()
    return env


@pytest.fixture
def ppo_agent(mock_store, mock_maskable_ppo, mock_env):
    """Create a PPOAgent with mocked dependencies"""
    # Mock the imported MaskablePPO class
    with (
        mock.patch("sb3_contrib.MaskablePPO.load", return_value=mock_maskable_ppo),
        mock.patch.object(PPOAgent, "get_env", return_value=mock_env),
    ):
        # Configure settings for PPO agent
        mock_store.settings.ppo_use_existing_model = True
        mock_store.settings.ppo_model_path = "test_model.zip"
        mock_store.settings.ppo_steps_per_iteration = 1000

        # Create the PPO agent
        agent = PPOAgent(mock_store)

        return agent


def test_ppo_agent_initialization(ppo_agent, mock_store, mock_maskable_ppo):
    """Test PPOAgent initialization"""
    # Verify the agent was initialized correctly
    assert ppo_agent.store == mock_store
    assert ppo_agent.model == mock_maskable_ppo


def test_ppo_agent_find_new_base_solution(ppo_agent, mock_store, different_solution):
    """Test that find_new_base_solution delegates to TabuAgent"""
    # Mock the TabuAgent.find_new_base_solution method
    with mock.patch.object(TabuAgent, "find_new_base_solution", return_value=different_solution) as mock_find:
        # Create a solution try
        solution_try = (FRONT_STATUS.IN_FRONT, different_solution)

        # Call find_new_base_solution
        result = ppo_agent.find_new_base_solution(solution_try)

        # Verify that TabuAgent's find_new_base_solution was called and the result returned
        assert result == different_solution
        mock_find.assert_called_once_with(solution_try)


def test_ppo_agent_select_actions_no_actions(ppo_agent, mock_store):
    """Test select_actions when no actions are available"""
    # Mock PPOInput.get_actions_from_store to return only None values
    with mock.patch(
        "o2.ppo_utils.ppo_input.PPOInput.get_actions_from_store", return_value=[None, None, None]
    ):
        # Call select_actions and expect NoActionsLeftError
        with pytest.raises(NoActionsLeftError):
            ppo_agent.select_actions()


def test_ppo_agent_select_actions_with_actions(ppo_agent, mock_store, mock_action):
    """Test select_actions with available actions"""
    # Mock PPOInput methods
    with (
        mock.patch(
            "o2.ppo_utils.ppo_input.PPOInput.get_actions_from_store", return_value=[mock_action, None, None]
        ),
        mock.patch(
            "o2.ppo_utils.ppo_input.PPOInput.get_action_mask_from_actions", return_value=np.array([1, 0, 0])
        ),
    ):
        # Mock policy to return action index 0
        actions = th.tensor([0])
        values = th.tensor([1.0])
        log_probs = th.tensor([0.5])
        ppo_agent.model.policy.return_value = (actions, values, log_probs)

        # Call select_actions
        result = ppo_agent.select_actions()

        # Verify the result
        assert len(result) == 1
        assert result[0] == mock_action

        # Verify the model state was updated
        np.testing.assert_array_equal(ppo_agent.last_actions, actions.numpy())
        np.testing.assert_array_equal(ppo_agent.last_values, values.numpy())
        np.testing.assert_array_equal(ppo_agent.log_probs, log_probs.numpy())


def test_ppo_agent_select_actions_invalid_action_index(ppo_agent, mock_store):
    """Test select_actions when the action index points to None"""
    # Mock PPOInput methods
    with (
        mock.patch("o2.ppo_utils.ppo_input.PPOInput.get_actions_from_store", return_value=[None, None, None]),
        mock.patch(
            "o2.ppo_utils.ppo_input.PPOInput.get_action_mask_from_actions", return_value=np.array([0, 0, 0])
        ),
    ):
        # Mock policy to return action index 0 (which is None)
        actions = th.tensor([0])
        values = th.tensor([1.0])
        log_probs = th.tensor([0.5])
        ppo_agent.model.policy.return_value = (actions, values, log_probs)

        # Call select_actions and expect NoActionsLeftError to be raised
        with pytest.raises(NoActionsLeftError):
            ppo_agent.select_actions()


def test_ppo_agent_process_many_solutions(ppo_agent, mock_store, better_solution):
    """Test process_many_solutions calls _result_callback"""
    # Mock the parent's process_many_solutions method
    with (
        mock.patch("o2.agents.agent.Agent.process_many_solutions") as mock_process,
        mock.patch.object(ppo_agent, "_result_callback") as mock_callback,
    ):
        # Set up the return value for mock_process
        chosen_tries = [(FRONT_STATUS.IN_FRONT, better_solution)]
        not_chosen_tries = []
        mock_process.return_value = (chosen_tries, not_chosen_tries)

        # Call process_many_solutions
        result = ppo_agent.process_many_solutions([better_solution])

        # Verify the result and that _result_callback was called
        assert result == (chosen_tries, not_chosen_tries)
        mock_callback.assert_called_once_with(chosen_tries, not_chosen_tries)


def test_ppo_agent_result_callback_with_step_info_from_try(ppo_agent, mock_store, better_solution):
    """Test _result_callback uses step_info_from_try correctly"""
    # Create a valid observation state
    valid_state = {"state": np.zeros(5)}

    # Mock the update_state method to set the necessary attributes
    def mock_update_state():
        ppo_agent.state = valid_state
        ppo_agent.actions = [mock.MagicMock(spec=BaseAction), None, None]

    with (
        mock.patch.object(ppo_agent, "update_state", side_effect=mock_update_state),
        mock.patch("o2.agents.ppo_agent.print_l1"),  # Suppress print statements
    ):
        # Set up the model state for _result_callback
        ppo_agent.last_actions = np.array([0])
        ppo_agent.last_values = np.array([1.0])
        ppo_agent.log_probs = np.array([0.5])
        ppo_agent.last_action_mask = np.array([1, 0, 0])

        # Mock PyTorch tensor conversion to avoid actual tensor operations
        with mock.patch("torch.as_tensor", return_value=th.zeros(5)):
            with mock.patch.object(ppo_agent.model.policy, "predict_values", return_value=th.tensor([0.5])):
                # Call _result_callback with a chosen solution
                chosen_tries = [(FRONT_STATUS.IN_FRONT, better_solution)]
                not_chosen_tries = []
                ppo_agent._result_callback(chosen_tries, not_chosen_tries)

                # Verify update_state was called
                ppo_agent.update_state.assert_called_once()

                # Verify rollout_buffer.add was called
                ppo_agent.model.rollout_buffer.add.assert_called_once()

                # Verify _last_obs was updated with the state from update_state
                assert ppo_agent.model._last_obs == valid_state


def test_ppo_agent_result_callback_train_when_buffer_full(ppo_agent, mock_store, better_solution):
    """Test _result_callback trains when the buffer is full"""
    # Create a valid observation state
    valid_state = {"state": np.zeros(5)}

    # Mock the update_state method to set the necessary attributes
    def mock_update_state():
        ppo_agent.state = valid_state
        ppo_agent.actions = [mock.MagicMock(spec=BaseAction), None, None]

    with (
        mock.patch.object(ppo_agent, "update_state", side_effect=mock_update_state),
        mock.patch("o2.agents.ppo_agent.print_l1"),  # Suppress print statements
    ):
        # Set up the model state
        ppo_agent.last_actions = np.array([0])
        ppo_agent.last_values = np.array([1.0])
        ppo_agent.log_probs = np.array([0.5])
        ppo_agent.last_action_mask = np.array([1, 0, 0])

        # Set rollout_buffer.full to True
        ppo_agent.model.rollout_buffer.full = True

        # Mock PyTorch tensor conversion to avoid actual tensor operations
        with mock.patch("torch.as_tensor", return_value=th.zeros(5)):
            with mock.patch.object(ppo_agent.model.policy, "predict_values", return_value=th.tensor([0.5])):
                # Call _result_callback
                chosen_tries = [(FRONT_STATUS.IN_FRONT, better_solution)]
                not_chosen_tries = []
                ppo_agent._result_callback(chosen_tries, not_chosen_tries)

                # Verify train was called
                ppo_agent.model.train.assert_called_once()
                # Verify rollout_buffer was reset
                ppo_agent.model.rollout_buffer.reset.assert_called_once()


def test_ppo_agent_step_info_from_try_reward_assignment(ppo_agent, mock_store):
    """Test step_info_from_try assigns the correct rewards based on solution status"""
    # Create test cases for different solution statuses
    test_cases = [
        (FRONT_STATUS.INVALID, -1),  # Invalid solutions get -1 reward
        (FRONT_STATUS.IN_FRONT, 1),  # Solutions in front get +1 reward
        (FRONT_STATUS.IS_DOMINATED, 10),  # Dominated solutions get +10 reward
        (FRONT_STATUS.DOMINATES, -1),  # Default case gets -1 reward
    ]

    # Create a valid observation state
    valid_state = {"state": np.zeros(5)}

    # Mock solution for testing
    solution = mock.MagicMock(spec=Solution)

    # Mock the update_state method to set the necessary attributes
    def mock_update_state():
        ppo_agent.state = valid_state
        ppo_agent.actions = [mock.MagicMock(spec=BaseAction), None, None]

    with (
        mock.patch.object(ppo_agent, "update_state", side_effect=mock_update_state),
        mock.patch("o2.agents.ppo_agent.print_l1"),  # Suppress print statements
    ):
        # Test each status
        for status, expected_reward in test_cases:
            solution_try = (status, solution)
            state, reward, done = ppo_agent.step_info_from_try(solution_try)

            # Verify the reward matches the expected value
            assert reward == expected_reward
            # Verify state is the one set by update_state
            assert state == valid_state
            # Verify update_state was called
            assert ppo_agent.update_state.call_count > 0


def test_ppo_agent_step_info_from_try_done_flag(ppo_agent, mock_store):
    """Test step_info_from_try sets done=True when no actions are available"""
    # Create a valid observation state
    valid_state = {"state": np.zeros(5)}

    # Mock solution for testing
    solution = mock.MagicMock(spec=Solution)

    # Test with no actions available
    def mock_update_state_no_actions():
        ppo_agent.state = valid_state
        ppo_agent.actions = [None, None, None]  # All None means no valid actions

    with (
        mock.patch.object(ppo_agent, "update_state", side_effect=mock_update_state_no_actions),
        mock.patch("o2.agents.ppo_agent.print_l1"),  # Suppress print statements
    ):
        solution_try = (FRONT_STATUS.IN_FRONT, solution)
        _, _, done = ppo_agent.step_info_from_try(solution_try)

        # Verify done is True when no actions are available
        assert done is True

    # Test with actions available
    def mock_update_state_with_actions():
        ppo_agent.state = valid_state
        ppo_agent.actions = [mock.MagicMock(spec=BaseAction), None, None]  # One valid action

    with (
        mock.patch.object(ppo_agent, "update_state", side_effect=mock_update_state_with_actions),
        mock.patch("o2.agents.ppo_agent.print_l1"),  # Suppress print statements
    ):
        solution_try = (FRONT_STATUS.IN_FRONT, solution)
        _, _, done = ppo_agent.step_info_from_try(solution_try)

        # Verify done is False when actions are available
        assert done is False
