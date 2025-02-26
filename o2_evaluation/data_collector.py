#!/usr/bin/env python3

import argparse
import os
from collections import defaultdict

import numpy as np
from typing_extensions import TypedDict

from o2.models.settings import AgentType, CostType, Settings
from o2.models.solution import Solution
from o2.optimizer import Optimizer
from o2.store import Store
from o2.util.logger import info, setup_logging
from o2.util.solution_dumper import SolutionDumper
from o2.util.stat_calculation_helper import (
    calculate_averaged_hausdorff_distance,
    calculate_delta_metric,
    calculate_hyperarea,
    calculate_purity,
    store_with_baseline_constraints,
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="CLI Tool for solving and analyzing simulation scenarios."
    )
    parser.add_argument(
        "--name",
        type=str,
        default=None,
        help="Name of the run (default: None). Used mainly for logs.",
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
        type=str,
        default="auto",
        help="Initial temperature for Simulated Annealing (either number or 'auto' for auto-estimation; default: 'auto')",
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
        "--max-batch-size",
        type=int,
        default=100,
        help="Maximum size of the batch (default: 100)",
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
    parser.add_argument(
        "--max-threads",
        type=int,
        default=os.cpu_count() or 1,
        help="Maximum number of threads (default: cpu_count)",
    )
    parser.add_argument(
        "--max-number-of-actions-to-select",
        type=int,
        default=None,
        help="Maximum number of actions to select (default: max-threads -- which is cpu_count by default)",
    )
    parser.add_argument(
        "--log-to-tensor-board",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Log to TensorBoard (default: False)",
    )
    parser.add_argument(
        "--archive-tensorboard-logs",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Archive TensorBoard logs",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Log to a file (default: None)",
    )
    parser.add_argument(
        "--log-level",
        type=str,
        default="DEBUG",
        help="Log level (default: DEBUG)",
    )
    return parser.parse_args()


class Metrics(TypedDict):
    """Metrics for the given store."""

    store_name: str
    number_of_solutions: int
    patreto_size: int
    hyperarea: float
    hyperarea_ratio: float
    hausdorff_distance: float
    delta: float
    purity: float


def calculate_metrics(
    stores: list[tuple[str, Store]], extra_solutions: list[Solution] = []
) -> list[Metrics]:
    """Calculate the metrics for the given stores."""
    all_solutions: list[Solution] = []
    for _, store in stores:
        solutions = [
            solution
            for solution in store.solution_tree.solution_lookup.values()
            if solution is not None
        ]
        all_solutions.extend(solutions)

    all_solutions.extend(extra_solutions)
    # Find the Pareto front (non-dominated solutions)
    all_solutions_front = [
        solution
        for solution in all_solutions
        if not any(
            solution.is_dominated_by(other)
            for other in all_solutions
            if other.point != solution.point
        )
    ]

    # Calculate the hyperarea (using the max cost and time as the center point)
    max_cost = max(solution.point[0] for solution in all_solutions)
    max_time = max(solution.point[1] for solution in all_solutions)
    center_point = (max_cost, max_time)
    global_hyperarea = calculate_hyperarea(all_solutions_front, center_point)

    metrics: list[Metrics] = []

    metrics.append(
        {
            "store_name": "Global",
            "number_of_solutions": len(all_solutions),
            "patreto_size": len(all_solutions_front),
            "hyperarea": global_hyperarea,
            "hyperarea_ratio": 0.0,
            "hausdorff_distance": 0.0,
            "delta": 0.0,
            "purity": 0.0,
        }
    )

    info("\n\nMetrics:")
    info("=========")
    info("Global Set:")
    info(f"\t> Solutions Total: {len(all_solutions)}")
    info(f"\t> Center Point: {center_point}")
    info(f"\t> Hyperarea: {global_hyperarea}")
    info("\t> Pareto front:")
    info(f"\t\t>> size: {len(all_solutions_front)}")
    info(
        f"\t\t>> Avg {Settings.get_pareto_x_label()}: {np.mean([sol.point[0] for sol in all_solutions_front])}"
    )
    info(
        f"\t\t>> Avg {Settings.get_pareto_y_label()}: {np.mean([sol.point[1] for sol in all_solutions_front])}"
    )

    for name, store in stores:
        pareto_solutions = store.current_pareto_front.solutions
        pareto_hyperarea = calculate_hyperarea(pareto_solutions, center_point)
        ratio = 0.0 if global_hyperarea == 0.0 else pareto_hyperarea / global_hyperarea

        hausdorff_distance = calculate_averaged_hausdorff_distance(
            pareto_solutions, all_solutions_front
        )
        delta = calculate_delta_metric(pareto_solutions, all_solutions_front)
        purity = calculate_purity(pareto_solutions, all_solutions_front)

        info(f"Store: {name}")
        info(f"\t> Solutions Total: {store.solution_tree.total_solutions}")
        info(f"\t> Solutions explored: {store.solution_tree.discarded_solutions}")
        info(f"\t> Solutions left: {store.solution_tree.solutions_left}")
        info("\t> Pareto front:")
        info(f"\t\t>> size: {store.current_pareto_front.size}")
        info(
            f"\t\t>> Avg {Settings.get_pareto_x_label()}: {store.current_pareto_front.avg_x}"
        )
        info(
            f"\t\t>> Avg {Settings.get_pareto_y_label()}: {store.current_pareto_front.avg_y}"
        )
        info(f"\t> Hyperarea: {pareto_hyperarea}")
        info(f"\t> Hyperarea Ratio: {ratio}")
        info(f"\t> Averaged Hausdorff Distance: {hausdorff_distance}")
        info(f"\t> Delta Metric: {delta}")
        info(f"\t> Purity Metric: {purity}")

        metrics.append(
            {
                "store_name": name,
                "number_of_solutions": store.solution_tree.total_solutions,
                "patreto_size": store.current_pareto_front.size,
                "hyperarea": pareto_hyperarea,
                "hyperarea_ratio": ratio,
                "hausdorff_distance": hausdorff_distance,
                "delta": delta,
                "purity": purity,
            }
        )

    return metrics


def update_store_settings(
    store: Store,
    agent: AgentType,
    max_iterations: int,
    max_non_improving_actions: int,
    max_threads: int,
    max_number_of_actions_to_select: int,
    log_to_tensor_board: bool,
) -> None:
    """Update the store settings for the given agent."""
    store.settings.optimos_legacy_mode = False
    store.settings.batching_only = True
    store.settings.max_iterations = max_iterations
    store.settings.max_non_improving_actions = max_non_improving_actions
    store.settings.agent = agent
    store.settings.max_threads = max_threads
    store.settings.max_number_of_actions_to_select = max_number_of_actions_to_select
    store.settings.log_to_tensor_board = log_to_tensor_board


def persist_store(store: Store) -> None:
    """Persist the store to a file."""
    SolutionDumper.instance.dump_store(store)


def solve_store(store: Store, dump_interval: int) -> None:
    """Solve the store with the given agent."""
    # Persist the initial state of the store
    persist_store(store)
    optimizer = Optimizer(store)
    generator = optimizer.get_iteration_generator(yield_on_non_acceptance=True)
    iteration = 1
    print(f"Start processing of {store.name}")
    for _ in generator:
        if store.settings.log_to_tensor_board:
            from o2.util.tensorboard_helper import TensorBoardHelper

            TensorBoardHelper.instance.tensor_board_iteration_callback(store.solution)
        if iteration % dump_interval == 0:
            persist_store(store)
        iteration += 1

    persist_store(store)
    if not store.settings.disable_parallel_evaluation:
        optimizer.executor.shutdown()


def collect_data_sequentially(base_store: Store, args) -> None:
    """Collect all possible solutions and the respective Pareto fronts."""
    info("Setting up Store")
    # Set some global settings
    Settings.SHOW_SIMULATION_ERRORS = True
    Settings.RAISE_SIMULATION_ERRORS = False
    Settings.COST_TYPE = CostType.WAITING_TIME_AND_PROCESSING_TIME
    Settings.DUMP_DISCARDED_SOLUTIONS = True
    Settings.NUMBER_OF_CASES = args.number_of_cases
    Settings.ARCHIVE_TENSORBOARD_LOGS = args.archive_tensorboard_logs
    Settings.ARCHIVE_SOLUTIONS = True
    Settings.DELETE_LOADED_SOLUTION_ARCHIVES = False

    # Optionally archive previous TensorBoard logs
    if (
        base_store.settings.log_to_tensor_board or args.log_to_tensor_board
    ) and Settings.ARCHIVE_TENSORBOARD_LOGS:
        from o2.util.tensorboard_helper import TensorBoardHelper

        TensorBoardHelper.move_logs_to_archive_dir()

    stores_to_run = []

    # Use TABU search
    if "Tabu Search" in args.models:
        tabu_store = Store.from_state_and_constraints(
            base_store.base_state,
            base_store.constraints,
            f"Tabu Search {base_store.name}",
        )
        update_store_settings(
            tabu_store,
            AgentType.TABU_SEARCH,
            args.max_iterations,
            args.max_non_improving_actions,
            args.max_threads,
            args.max_number_of_actions_to_select or args.max_threads,
            args.log_to_tensor_board,
        )
        solve_store(tabu_store, args.dump_interval)
        stores_to_run.append(("Tabu Search", tabu_store))

    # Use Simulated Annealing
    if "Simulated Annealing" in args.models:
        sa_store = Store.from_state_and_constraints(
            base_store.base_state,
            base_store.constraints,
            f"Simulated Annealing {base_store.name}",
        )
        update_store_settings(
            sa_store,
            AgentType.SIMULATED_ANNEALING,
            args.max_iterations,
            args.max_non_improving_actions,
            args.max_threads,
            args.max_number_of_actions_to_select or args.max_threads,
            args.log_to_tensor_board,
        )
        sa_store.settings.sa_initial_temperature = (
            float(args.sa_initial_temperature)
            if args.sa_initial_temperature != "auto"
            else "auto"
        )
        sa_store.settings.sa_cooling_factor = args.sa_cooling_factor
        solve_store(sa_store, args.dump_interval)
        stores_to_run.append(("Simulated Annealing", sa_store))

    # Use Proximal Policy Optimization (PPO)
    if "Proximal Policy Optimization" in args.models:
        ppo_store = Store.from_state_and_constraints(
            base_store.base_state,
            base_store.constraints,
            f"Proximal Policy Optimization {base_store.name}",
        )
        update_store_settings(
            ppo_store,
            AgentType.PROXIMAL_POLICY_OPTIMIZATION,
            args.max_iterations,
            args.max_non_improving_actions,
            args.max_threads,
            args.max_number_of_actions_to_select or args.max_threads,
            args.log_to_tensor_board,
        )
        ppo_store.settings.disable_parallel_evaluation = True
        ppo_store.settings.max_threads = 1
        ppo_store.settings.max_number_of_actions_to_select = 1
        solve_store(ppo_store, args.dump_interval)
        stores_to_run.append(("Proximal Policy Optimization", ppo_store))

    # Calculate and print metrics
    calculate_metrics(stores_to_run, SolutionDumper.instance.load_solutions())

    SolutionDumper.instance.close()


if __name__ == "__main__":
    # Parse CLI arguments
    args = parse_args()

    Settings.LOG_LEVEL = args.log_level
    Settings.LOG_FILE = args.log_file if args.log_file else None

    setup_logging()

    # Initialize the solution dumper
    SolutionDumper()

    # Loop over the active scenarios provided via CLI
    for scenario in args.active_scenarios:
        if scenario == "Demo":
            from o2_evaluation.scenarios.demo.demo_model import demo_store

            store = demo_store
        else:
            scenario_folder = "o2_evaluation/scenarios"

            if scenario == "Purchasing":
                timetable_path = (
                    f"{scenario_folder}/purchasing_example/purchasing_example.json"
                )
                bpmn_path = (
                    f"{scenario_folder}/purchasing_example/purchasing_example.bpmn"
                )
            elif scenario == "TwoTasks":
                timetable_path = "examples/two_tasks_batching/two_tasks_batching.json"
                bpmn_path = "examples/two_tasks_batching/two_tasks_batching.bpmn"
            else:
                timetable_path = f"{scenario_folder}/{scenario}/{scenario}.json"
                bpmn_path = f"{scenario_folder}/{scenario}/{scenario}.bpmn"
                # Check if the files exist
                if not os.path.exists(timetable_path):
                    raise FileNotFoundError(
                        f"Unknown scenario: {scenario}. Please check the scenario folder."
                    )
                if not os.path.exists(bpmn_path):
                    raise FileNotFoundError(
                        f"Unknown scenario: {scenario}. Please check the scenario folder."
                    )

            info(f"Loaded Scenario {scenario}")

            if args.name:
                name = args.name
            else:
                name = scenario.replace("-", "_").replace(" ", "_").lower()

            # Pass the cost and duration functions from CLI arguments.
            store = store_with_baseline_constraints(
                timetable_path,
                bpmn_path,
                args.duration_fn,
                args.cost_fn,
                args.max_batch_size,
                name,
            )

        # Run the simulation/collection for the current scenario
        collect_data_sequentially(store, args)
