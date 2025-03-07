from o2.agents.agent import ACTION_CATALOG_LEGACY, ACTION_CATALOG_RANDOM
from o2.agents.tabu_agent import TabuAgent
from o2.store import Store


class TabuAgentRandom(TabuAgent):
    """TabuAgentRandom is a TabuAgent that selects actions randomly."""

    def __init__(self, store: Store) -> None:
        super().__init__(store)

        store.settings.disable_action_validity_check = True
        self.catalog = ACTION_CATALOG_RANDOM
