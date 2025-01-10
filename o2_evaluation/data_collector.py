import numpy as np

from o2.hill_climber import HillClimber
from o2.models.settings import AgentType, CostType, Settings
from o2.models.solution import Solution
from o2.store import Store
from o2_evaluation.scenarios.demo.demo_model import demo_store

MAX_ITERATIONS = 100
MAX_NON_IMPROVING_ACTIONS = 50


def calculate_hyperarea(solutions: list[Solution], center_point):
    """Calculate the hyperarea covered by a set of solutions relative to a center point."""
    total_area = 0.0
    for solution in solutions:
        x, y = solution.point
        area = (center_point[0] - x) * (center_point[1] - y)
        if area > 0:  # Ignore invalid solutions
            total_area += area
    return total_area


def distance(point1, point2):
    return np.linalg.norm(np.array(point1) - np.array(point2))


def calculate_averaged_hausdorff_distance(
    pareto_front: list[Solution], global_set: list[Solution]
):
    """Calculate the Averaged Hausdorff Distance between the Pareto front and the global set."""

    total_distance = 0.0
    for solution in pareto_front:
        distances = [distance(solution.point, other.point) for other in global_set]
        total_distance += min(distances)

    # Average over the Pareto front size
    return total_distance / len(pareto_front) if pareto_front else 0.0


def calculate_delta_metric(pareto_front: list[Solution], global_set: list[Solution]):
    """Calculate the Delta metric for diversity of the Pareto front."""
    if not pareto_front:
        return 0.0

    distances = [
        np.linalg.norm(np.array(p1.point) - np.array(p2.point))
        for i, p1 in enumerate(pareto_front)
        for j, p2 in enumerate(pareto_front)
        if i < j
    ]

    avg_distance = np.mean(distances) if distances else 0.0
    return np.std(distances) / avg_distance if avg_distance > 0 else 0.0


def calculate_purity(pareto_front: list[Solution], global_set: list[Solution]) -> float:
    """Calculate the Purity metric for the Pareto front."""
    pareto_set = {tuple(sol.point) for sol in pareto_front}
    global_set_points = {tuple(sol.point) for sol in global_set}
    pure_points = pareto_set.intersection(global_set_points)
    return len(pure_points) / len(pareto_front) if pareto_front else 0.0


def calculate_metrics(stores: list[tuple[str, Store]]):
    """Calculate the metrics for the given stores."""
    all_solutions: list[Solution] = []
    for _, store in stores:
        solutions = [
            solution
            for solution in store.solution_tree.solution_lookup.values()
            if solution is not None
        ] + (store.solution_tree.evaluation_discarded_solutions or [])
        all_solutions.extend(solutions)

    # Find pareto front for all solutions
    all_solutions_front = [
        solution
        for solution in all_solutions
        if not any(solution.is_dominated_by(other) for other in all_solutions)
    ]

    # Calculate hyperarea

    # Find the center point
    max_cost = max(solution.point[0] for solution in all_solutions)
    max_time = max(solution.point[1] for solution in all_solutions)
    center_point = (max_cost, max_time)

    # Calculate hyperarea for global set and Pareto front
    global_hyperarea = calculate_hyperarea(all_solutions_front, center_point)
    print("\n\nMetrics:")
    print("=========")
    print("Global Set:")
    print(f"\t> Solutions Total: {len(all_solutions)}")
    print(f"\t> Center Point: {center_point}")
    print(f"\t> Hyperarea: {global_hyperarea}")
    # Global pareto
    print("\t> Pareto front:")
    print(f"\t\t>> size: {len(all_solutions_front)}")
    print(f"\t\t>> Avg cost: {np.mean([sol.point[0] for sol in all_solutions_front])}")
    print(f"\t\t>> Avg time: {np.mean([sol.point[1] for sol in all_solutions_front])}")

    for name, store in stores:
        pareto_solutions = store.current_pareto_front.solutions
        pareto_hyperarea = calculate_hyperarea(pareto_solutions, center_point)

        # Hyperarea ratio
        ratio = 0.0 if global_hyperarea == 0.0 else pareto_hyperarea / global_hyperarea

        hausdorff_distance = calculate_averaged_hausdorff_distance(
            pareto_solutions, all_solutions_front
        )
        delta = calculate_delta_metric(pareto_solutions, all_solutions_front)
        purity = calculate_purity(pareto_solutions, all_solutions_front)

        print(f"Store: {name}")
        print(f"\t> Solutions Total: {store.solution_tree.total_solutions}")
        print(f"\t> Solutions explored: {store.solution_tree.discarded_solutions}")
        print(f"\t> Solutions left: {store.solution_tree.solutions_left}")
        print("\t> Pareto front:")
        print(f"\t\t>> size: {store.current_pareto_front.size}")
        print(f"\t\t>> Avg cost: {store.current_pareto_front.avg_total_cost}")
        print(f"\t\t>> Avg time: {store.current_pareto_front.avg_total_duration}")
        print(f"\t> Hyperarea: {pareto_hyperarea}")
        print(f"\t> Hyperarea Ratio: {ratio}")
        print(f"\t> Averaged Hausdorff Distance: {hausdorff_distance}")
        print(f"\t> Delta Metric: {delta}")
        print(f"\t> Purity Metric: {purity}")


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
