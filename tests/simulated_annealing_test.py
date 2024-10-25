from o2.hill_climber import HillClimber
from o2.models.settings import AgentType
from o2.store import Store


def test_simulated_annealing(one_task_store: Store):
    store = one_task_store

    store.settings.agent = AgentType.SIMULATED_ANNEALING
    store.settings.sa_initial_temperature = 5_000_000_000
    store.settings.sa_cooling_factor = 0.90

    hill_climber = HillClimber(store)
    hill_climber.solve()
