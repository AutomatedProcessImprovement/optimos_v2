from unittest.mock import patch


from o2.agents.ppo_agent import PPOAgent
from o2.models.settings import AgentType, CostType, Settings
from o2.optimizer import Optimizer
from o2.store import Store


def test_ppo_agent_optimizer_integration(one_task_store: Store):
    Settings.COST_TYPE = CostType.TOTAL_COST
    store = one_task_store

    store.settings.agent = AgentType.PROXIMAL_POLICY_OPTIMIZATION
    store.settings.ppo_use_existing_model = False
    store.settings.ppo_steps_per_iteration = 50
    store.settings.max_iterations = 100

    # Mock the MaskablePPO to avoid actual training
    with patch("sb3_contrib.MaskablePPO"):
        optimizer = Optimizer(store)

        # Test that the optimizer correctly initialized a PPOAgent
        assert isinstance(optimizer.agent, PPOAgent)

        # Test the PPOAgent was initialized with the right settings
        assert store.settings.ppo_steps_per_iteration == 50
        assert store.settings.max_iterations == 100
