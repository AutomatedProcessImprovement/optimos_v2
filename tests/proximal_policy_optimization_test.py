import math

import pytest

from o2.agents.simulated_annealing_agent import SimulatedAnnealingAgent
from o2.models.settings import AgentType
from o2.optimizer import Optimizer
from o2.store import Store


def test_proximal_policy_optimization(one_task_store: Store):
    store = one_task_store
    store.settings.max_iterations = 2

    store.settings.agent = AgentType.PROXIMAL_POLICY_OPTIMIZATION

    optimizer = Optimizer(store)
    optimizer.solve()
