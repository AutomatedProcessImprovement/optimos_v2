
from o2.agents.agent import ACTION_CATALOG_RANDOM
from o2.agents.tabu_agent_random import TabuAgentRandom
from o2.models.settings import AgentType, CostType, Settings
from o2.optimizer import Optimizer
from o2.store import Store


def test_tabu_search_random(one_task_store: Store):
    Settings.COST_TYPE = CostType.TOTAL_COST
    store = one_task_store

    store.settings.agent = AgentType.TABU_SEARCH_RANDOM
    store.settings.max_distance_to_new_base_solution = 100

    optimizer = Optimizer(store)

    assert isinstance(optimizer.agent, TabuAgentRandom)
    assert store.settings.disable_action_validity_check is True

    # Verify the catalog has been set to random actions
    assert optimizer.agent.catalog == ACTION_CATALOG_RANDOM
