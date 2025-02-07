#!/usr/bin/env python3
import argparse
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


def parse_args():
    parser = argparse.ArgumentParser(
        description="CLI Tool for solving and analyzing simulation scenarios."
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=1500,
        help="Maximum number of iterations (default: 1500)",
    )
    parser.add_argument(
        "--max-non-improving-actions",
        type=int,
        default=(os.cpu_count() or 1) * 100,
        help="Maximum number of non-improving actions (default: cpu_count*100)",
    )
    parser.add_argument(
        "--dump-interval",
        type=int,
        default=250,
        help="Interval for dumping solution data (default: 250)",
    )
    parser.add_argument(
        "--active-scenarios",
        type=str,
        nargs="+",
        default=["BPI_Challenge_2017"],
        help="List of active scenarios (e.g. Demo, Purchasing, BPI_Challenge_2017, TwoTasks)",
    )
    parser.add_argument(
        "--sa-initial-temperature",
        type=int,
        default=75000000,
        help="Initial temperature for Simulated Annealing (default: 75000000)",
    )
    parser.add_argument(
        "--sa-cooling-factor",
        type=float,
        default=0.995,
        help="Cooling factor for Simulated Annealing (default: 0.995)",
    )
    parser.add_argument(
        "--fixed-cost-fn",
        type=str,
        default="1 * 1/size",
        help="Fixed cost function (default: '1 * 1/size')",
    )
    parser.add_argument(
        "--cost-fn",
        type=str,
        default="1",
        help="Cost function (default: '1')",
    )
    parser.add_argument(
        "--duration-fn",
        type=str,
        default="1/size",
        help="Duration function (default: '1/size')",
    )
    parser.add_argument(
        "--number-of-cases",
        type=int,
        default=100,
        help="Number of cases (default: 100)",
    )
    parser.add_argument(
        "--models",
        type=str,
        nargs="+",
        default=["Tabu Search", "Simulated Annealing", "Proximal Policy Optimization"],
        help="List of models to run (e.g. 'Tabu Search', 'Simulated Annealing', 'Proximal Policy Optimization')",
    )
    return parser.parse_args()


def calculate_metrics(stores: list[tuple[str, Store]]) -> None:
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

    # Find the Pareto front (non-dominated solutions)
    all_solutions_front = [
        solution
        for solution in all_solutions
        if not any(solution.is_dominated_by(other) for other in all_solutions)
    ]

    # Calculate the hyperarea (using the max cost and time as the center point)
    max_cost = max(solution.point[0] for solution in all_solutions)
    max_time = max(solution.point[1] for solution in all_solutions)
    center_point = (max_cost, max_time)
    global_hyperarea = calculate_hyperarea(all_solutions_front, center_point)

    print("\n\nMetrics:")
    print("=========")
    print("Global Set:")
    print(f"\t> Solutions Total: {len(all_solutions)}")
    print(f"\t> Center Point: {center_point}")
    print(f"\t> Hyperarea: {global_hyperarea}")
    print("\t> Pareto front:")
    print(f"\t\t>> size: {len(all_solutions_front)}")
    print(f"\t\t>> Avg cost: {np.mean([sol.point[0] for sol in all_solutions_front])}")
    print(f"\t\t>> Avg time: {np.mean([sol.point[1] for sol in all_solutions_front])}")

    for name, store in stores:
        pareto_solutions = store.current_pareto_front.solutions
        pareto_hyperarea = calculate_hyperarea(pareto_solutions, center_point)
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


def update_store_settings(
    store: Store, agent: AgentType, max_iterations: int, max_non_improving_actions: int
) -> None:
    """Update the store settings for the given agent."""
    store.settings.optimos_legacy_mode = False
    store.settings.batching_only = True
    store.settings.max_iterations = max_iterations
    store.settings.max_non_improving_actions = max_non_improving_actions
    store.settings.agent = agent


def persist_store(store: Store) -> None:
    """Persist the store to a file."""
    SolutionDumper.instance.dump_store(store)


def solve_store(store: Store, dump_interval: int) -> None:
    """Solve the store with the given agent."""
    hill_climber = HillClimber(store)
    generator = hill_climber.get_iteration_generator(yield_on_non_acceptance=True)
    iteration = 1
    for _ in generator:
        if store.settings.log_to_tensor_board:
            TensorBoardHelper.instance.tensor_board_iteration_callback(store.solution)
        if iteration % dump_interval == 0:
            persist_store(store)
        iteration += 1

    persist_store(store)
    if not store.settings.disable_parallel_evaluation:
        hill_climber.executor.shutdown()


def collect_data_sequentially(base_store: Store, args) -> None:
    """Collect all possible solutions and the respective Pareto fronts."""
    print("Setting up Store")
    # Set some global settings
    Settings.SHOW_SIMULATION_ERRORS = True
    Settings.RAISE_SIMULATION_ERRORS = False
    Settings.COST_TYPE = CostType.WAITING_TIME_AND_PROCESSING_TIME
    Settings.DUMP_DISCARDED_SOLUTIONS = True
    Settings.NUMBER_OF_CASES = args.number_of_cases

    # Initialize the solution dumper
    SolutionDumper()

    # Optionally archive previous TensorBoard logs
    if base_store.settings.log_to_tensor_board:
        TensorBoardHelper.move_logs_to_archive_dir()

    stores_to_run = []

    # Use TABU search
    if "Tabu Search" in args.models:
        tabu_store = Store.from_state_and_constraints(
            base_store.base_state, base_store.constraints, "Tabu Search"
        )
        update_store_settings(
            tabu_store,
            AgentType.TABU_SEARCH,
            args.max_iterations,
            args.max_non_improving_actions,
        )
        solve_store(tabu_store, args.dump_interval)
        stores_to_run.append(("Tabu Search", tabu_store))

    # Use Simulated Annealing
    if "Simulated Annealing" in args.models:
        sa_store = Store.from_state_and_constraints(
            base_store.base_state, base_store.constraints, "Simulated Annealing"
        )
        update_store_settings(
            sa_store,
            AgentType.SIMULATED_ANNEALING,
            args.max_iterations,
            args.max_non_improving_actions,
        )
        sa_store.settings.sa_initial_temperature = args.sa_initial_temperature
        sa_store.settings.sa_cooling_factor = args.sa_cooling_factor
        solve_store(sa_store, args.dump_interval)
        stores_to_run.append(("Simulated Annealing", sa_store))

    # Use Proximal Policy Optimization (PPO)
    if "Proximal Policy Optimization" in args.models:
        ppo_store = Store.from_state_and_constraints(
            base_store.base_state,
            base_store.constraints,
            "Proximal Policy Optimization",
        )
        update_store_settings(
            ppo_store,
            AgentType.PROXIMAL_POLICY_OPTIMIZATION,
            args.max_iterations,
            args.max_non_improving_actions,
        )
        ppo_store.settings.disable_parallel_evaluation = True
        ppo_store.settings.max_threads = 1
        solve_store(ppo_store, args.dump_interval)
        stores_to_run.append(("Proximal Policy Optimization", ppo_store))

    # Calculate and print metrics
    calculate_metrics(stores_to_run)

    SolutionDumper.instance.close()


if __name__ == "__main__":
    # Parse CLI arguments
    args = parse_args()

    # Loop over the active scenarios provided via CLI
    for scenario in args.active_scenarios:
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

            print(f"Loaded Scenario {scenario}")

            # Pass the cost and duration functions from CLI arguments.
            store = store_with_baseline_constraints(
                timetable_path, bpmn_path, args.duration_fn, args.cost_fn
            )
        # Run the simulation/collection for the current scenario
        collect_data_sequentially(store, args)
