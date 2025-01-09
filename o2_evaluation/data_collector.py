def calculate_hyperarea(solutions: list[Solution], center_point):
    """Calculate the hyperarea covered by a set of solutions relative to a center point."""
    total_area = 0.0
    for solution in solutions:
        x, y = solution.point
        area = (center_point[0] - x) * (center_point[1] - y)
        if area > 0:  # Ignore invalid solutions
            total_area += area
    return total_area



def update_store_settings(store: Store, agent: AgentType):
    """Update the store settings for the given agent."""
    store.settings.optimos_legacy_mode = False
    store.settings.batching_only = True
    store.settings.max_iterations = MAX_ITERATIONS
    store.settings.max_non_improving_actions = MAX_NON_IMPROVING_ACTIONS

    store.settings.agent = agent


def collect_data_sequentially():
    """Collect all possible solutions, and the respective pareto fronts.

    It does this sequentially for the 3 simulation methods one after the other.
    """
    # Make sure we use FIXED cost type
    Settings.COST_TYPE = CostType.FIXED_COST
    Settings.DO_NOT_DISCARD_SOLUTIONS = True

    # We start with TABU search

    # Clone store just to avoid changing the original store
    tabu_store = Store.from_state_and_constraints(
        demo_store.base_state, demo_store.constraints
    )
    update_store_settings(tabu_store, AgentType.TABU_SEARCH)

    tabu_climber = HillClimber(tabu_store)
    tabu_climber.solve()

    # Next, we use Simulated Annealing
    sa_store = Store.from_state_and_constraints(
        demo_store.base_state, demo_store.constraints
    )
    update_store_settings(sa_store, AgentType.SIMULATED_ANNEALING)
    sa_store.settings.sa_initial_temperature = 5_000_000_000
    sa_store.settings.sa_cooling_factor = 0.90

    sa_climber = HillClimber(sa_store)
    sa_climber.solve()

    # Finally we use PPO
    # ppo_store = Store.from_state_and_constraints(
    #     demo_store.base_state, demo_store.constraints
    # )
    # update_store_settings(ppo_store, AgentType.PROXIMAL_POLICY_OPTIMIZATION)

    # ppo_climber = HillClimber(ppo_store)
    # ppo_climber.solve()

    # Calculate metrics
    calculate_metrics(
        [
            ("Tabu Search", tabu_store),
            ("Simulated Annealing", sa_store),
            # ("Proximal Policy Optimization", ppo_store),
        ]
    )


if __name__ == "__main__":
    collect_data_sequentially()
