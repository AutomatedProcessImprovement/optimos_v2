
from o2.agents.agent import ACTION_CATALOG_RANDOM
from o2.agents.simulated_annealing_agent_random import SimulatedAnnealingAgentRandom
from o2.models.settings import AgentType, CostType, Settings
from o2.optimizer import Optimizer
from o2.store import Store


def test_simulated_annealing_random(one_task_store: Store):
    Settings.COST_TYPE = CostType.TOTAL_COST
    store = one_task_store

    store.settings.agent = AgentType.SIMULATED_ANNEALING_RANDOM
    store.settings.sa_initial_temperature = 1000
    store.settings.sa_cooling_factor = 0.95

    optimizer = Optimizer(store)

    assert isinstance(optimizer.agent, SimulatedAnnealingAgentRandom)
    assert store.settings.disable_action_validity_check is True

    # Verify temperature is set correctly
    assert optimizer.agent.temperature == 1000

    # Verify the catalog has been set to random actions
    assert optimizer.agent.catalog == ACTION_CATALOG_RANDOM
