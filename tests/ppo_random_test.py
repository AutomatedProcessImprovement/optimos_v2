from unittest.mock import patch


from o2.agents.ppo_agent_random import PPOAgentRandom
from o2.models.settings import AgentType, CostType, Settings
from o2.optimizer import Optimizer
from o2.store import Store


def test_ppo_random_optimizer_integration(one_task_store: Store):
    Settings.COST_TYPE = CostType.TOTAL_COST
    store = one_task_store

    store.settings.agent = AgentType.PROXIMAL_POLICY_OPTIMIZATION_RANDOM
    store.settings.ppo_use_existing_model = False
    store.settings.ppo_steps_per_iteration = 50
    store.settings.max_iterations = 100

    # Mock the MaskablePPO to avoid actual training
    with patch("sb3_contrib.MaskablePPO"):
        optimizer = Optimizer(store)

        # Test that the optimizer correctly initialized a PPOAgentRandom
        assert isinstance(optimizer.agent, PPOAgentRandom)

        # Test the PPOAgentRandom was initialized with the right settings
        assert store.settings.ppo_steps_per_iteration == 50
        assert store.settings.max_iterations == 100
        assert store.settings.disable_action_validity_check is True
