from o2.agents.agent import ACTION_CATALOG_RANDOM
from o2.agents.simulated_annealing_agent import SimulatedAnnealingAgent
from o2.store import Store


class SimulatedAnnealingAgentRandom(SimulatedAnnealingAgent):
    """SimulatedAnnealingAgentRandom is a SimulatedAnnealingAgent that selects actions randomly."""

    def __init__(self, store: Store) -> None:
        super().__init__(store)

        store.settings.disable_action_validity_check = True
        self.catalog = ACTION_CATALOG_RANDOM
