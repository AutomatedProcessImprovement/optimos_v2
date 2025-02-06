import json
import os
import xml.etree.ElementTree as ET

import numpy as np

from o2.hill_climber import HillClimber
from o2.models.constraints import ConstraintsType, SizeRuleConstraints
from o2.models.settings import AgentType, CostType, Settings
from o2.models.solution import Solution
from o2.models.state import State
from o2.models.timetable import BATCH_TYPE, RULE_TYPE, TimetableType
from o2.store import Store
from o2.util.solution_dumper import SolutionDumper
from o2.util.stat_calculation_helper import (
    calculate_averaged_hausdorff_distance,
    calculate_delta_metric,
    calculate_hyperarea,
    calculate_purity,
    store_with_baseline_constraints,
)
from o2.util.tensorboard_helper import TensorBoardHelper

MAX_ITERATIONS = 1500
# NOTE: This is actions(!) not iterations, therefore we need to set this
# to a higher value.  A good rule of thumb is to set it
# to core_count times the number of non improving iterations
MAX_NON_IMPROVING_ACTIONS = (os.cpu_count() or 1) * 100
DUMP_INTERVAL = 250
ACTIVE_SCENARIOS = ["BPI_Challenge_2017"]

SA_INITIAL_TEMPERATURE = 75_000_000
SA_COOLING_FACTOR = 0.995

FIXED_COST_FN = "1 * 1/size"
COST_FN = "1"
DURATION_FN = "1/size"

NUMBER_OF_CASES = 100


def calculate_metrics(stores: list[tuple[str, Store]]):
    """Calculate the metrics for the given stores."""
    all_solutions: list[Solution] = []
    for _, store in stores:
        solutions = [
            solution
            for solution in store.solution_tree.solution_lookup.values()
            if solution is not None
        ]
        all_solutions.extend(solutions)

    all_solutions.extend(SolutionDumper.instance.load_solutions())

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
        print(
            f"\t\t>> Avg {Settings.get_pareto_x_label()}: {store.current_pareto_front.avg_x}"
        )
        print(
            f"\t\t>> Avg {Settings.get_pareto_y_label()}: {store.current_pareto_front.avg_y}"
        )
        print(f"\t> Hyperarea: {pareto_hyperarea}")
        print(f"\t> Hyperarea Ratio: {ratio}")
        print(f"\t> Averaged Hausdorff Distance: {hausdorff_distance}")
        print(f"\t> Delta Metric: {delta}")
        print(f"\t> Purity Metric: {purity}")


def update_store_settings(store: Store, agent: AgentType) -> None:
    """Update the store settings for the given agent."""

    store.settings.optimos_legacy_mode = False
    store.settings.batching_only = True
    store.settings.max_iterations = MAX_ITERATIONS
    store.settings.max_non_improving_actions = MAX_NON_IMPROVING_ACTIONS

    store.settings.agent = agent


def persist_store(store: Store) -> None:
    """Persist the store to a file."""
    SolutionDumper.instance.dump_store(store)


def solve_store(store: Store) -> None:
    """Solve the store with the given agent."""
    hill_climber = HillClimber(store)
    generator = hill_climber.get_iteration_generator(yield_on_non_acceptance=True)
    iteration = 1
    for _ in generator:
        if store.settings.log_to_tensor_board:
            # Just iterate through the generator to run it
            TensorBoardHelper.instance.tensor_board_iteration_callback(store.solution)
        if iteration % DUMP_INTERVAL == 0:
            persist_store(store)
        iteration += 1

    persist_store(store)
    if not store.settings.disable_parallel_evaluation:
        hill_climber.executor.shutdown()


def collect_data_sequentially(base_store: Store) -> None:
    """Collect all possible solutions, and the respective pareto fronts.

    It does this sequentially for the 3 simulation methods one after the other.
    """
    print("Setting up enviorment")
    # Constant (class variable) settings
    Settings.SHOW_SIMULATION_ERRORS = True
    Settings.RAISE_SIMULATION_ERRORS = False
    Settings.COST_TYPE = CostType.WAITING_TIME_AND_PROCESSING_TIME
    Settings.DUMP_DISCARDED_SOLUTIONS = True
    Settings.NUMBER_OF_CASES = NUMBER_OF_CASES

    # Initialize solution dumper
    SolutionDumper()

    # Move TensorBoard logs to a new folder
    if base_store.settings.log_to_tensor_board:
        TensorBoardHelper.move_logs_to_archive_dir()

    # We start with TABU search

    # Clone store just to avoid changing the original store
    tabu_store = Store.from_state_and_constraints(
        base_store.base_state, base_store.constraints, "Tabu Search"
    )
    update_store_settings(tabu_store, AgentType.TABU_SEARCH)

    solve_store(tabu_store)

    # # Next, we use Simulated Annealing
    sa_store = Store.from_state_and_constraints(
        base_store.base_state, base_store.constraints, "Simulated Annealing"
    )
    update_store_settings(sa_store, AgentType.SIMULATED_ANNEALING)
    sa_store.settings.sa_initial_temperature = SA_INITIAL_TEMPERATURE
    sa_store.settings.sa_cooling_factor = SA_COOLING_FACTOR

    solve_store(sa_store)

    # Finally we use PPO
    ppo_store = Store.from_state_and_constraints(
        base_store.base_state, base_store.constraints, "Proximal Policy Optimization"
    )
    update_store_settings(ppo_store, AgentType.PROXIMAL_POLICY_OPTIMIZATION)
    ppo_store.settings.disable_parallel_evaluation = True
    ppo_store.settings.max_threads = 1

    solve_store(ppo_store)

    # Calculate metrics
    calculate_metrics(
        [
            ("Tabu Search", tabu_store),
            ("Simulated Annealing", sa_store),
            ("Proximal Policy Optimization", ppo_store),
        ]
    )

    SolutionDumper.instance.close()


if __name__ == "__main__":
    for scenario in ACTIVE_SCENARIOS:
        if scenario == "Demo":
            from o2_evaluation.scenarios.demo.demo_model import demo_store

            store = demo_store
        else:
            if scenario == "Purchasing":
                timetable_path = (
                    "o2_evaluation/scenarios/purchasing_example/purchasing_example.json"
                )
                bpmn_path = (
                    "o2_evaluation/scenarios/purchasing_example/purchasing_example.bpmn"
                )

            elif scenario == "BPI_Challenge_2017":
                timetable_path = (
                    "o2_evaluation/scenarios/bpi_challenge_2017/bpi_challenge_2017.json"
                )
                bpmn_path = (
                    "o2_evaluation/scenarios/bpi_challenge_2017/bpi_challenge_2017.bpmn"
                )

            elif scenario == "TwoTasks":
                timetable_path = "examples/two_tasks_batching/two_tasks_batching.json"
                bpmn_path = "examples/two_tasks_batching/two_tasks_batching.bpmn"

            else:
                raise ValueError(f"Unknown scenario: {scenario}")

            store = store_with_baseline_constraints(
                timetable_path, bpmn_path, DURATION_FN, COST_FN
            )
        collect_data_sequentially(store)
