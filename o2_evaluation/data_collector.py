#!/usr/bin/env python3

import argparse
import os

from o2.models.settings import ActionVariationSelection, AgentType, CostType, Settings
from o2.optimizer import Optimizer
from o2.store import Store
from o2.util.logger import info, setup_logging, stats
from o2.util.solution_dumper import SolutionDumper
from o2.util.stat_calculation_helper import (
    store_with_baseline_constraints,
)


def parse_args():
    parser = argparse.ArgumentParser(description="CLI Tool for solving and analyzing simulation scenarios.")
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
        "--iterations-per-solution",
        type=int,
        default=None,
        help="Number of iterations to run for each base solution (default: infinite)",
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
        type=str,
        default="auto",
        help="Cooling factor for Simulated Annealing (either number or 'auto' for auto-estimation; default: 'auto')",
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
        "--agents",
        type=str,
        nargs="+",
        default=[
            "Tabu Search",
            "Simulated Annealing",
            "Proximal Policy Optimization",
            "Tabu Search Random",
            "Simulated Annealing Random",
            "Proximal Policy Optimization Random",
        ],
        help="List of agents to run (e.g. 'Tabu Search', 'Simulated Annealing', 'Proximal Policy Optimization')",
    )
    parser.add_argument(
        "--max-threads",
        type=int,
        default=os.cpu_count() or 1,
        help="Maximum number of threads (default: cpu_count)",
    )
    parser.add_argument(
        "--max-number-of-actions-per-iteration",
        type=int,
        default=None,
        help="Maximum number of actions to select per iteration (default: max-threads -- which is cpu_count by default)",
    )
    parser.add_argument(
        "--max-number-of-variations-per-action",
        type=int,
        default=float("inf"),
        help="Maximum number of 'variations' per action (default: infinity). Can be used to make the search more local.",
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


def update_store_settings(
    store: Store,
    agent: AgentType,
    max_iterations: int,
    max_non_improving_actions: int,
    max_threads: int,
    max_number_of_actions_per_iteration: int,
    log_to_tensor_board: bool,
    iterations_per_solution: int,
) -> None:
    """Update the store settings for the given agent."""
    store.settings.optimos_legacy_mode = False
    store.settings.batching_only = True
    store.settings.max_iterations = max_iterations
    store.settings.max_non_improving_actions = max_non_improving_actions
    store.settings.agent = agent
    store.settings.max_threads = max_threads
    store.settings.max_number_of_actions_per_iteration = max_number_of_actions_per_iteration
    store.settings.log_to_tensor_board = log_to_tensor_board
    store.settings.iterations_per_solution = iterations_per_solution


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
    info(f"Start processing of {store.name}")
    for _ in generator:
        if store.settings.log_to_tensor_board:
            from o2.util.tensorboard_helper import TensorBoardHelper

            TensorBoardHelper.instance.tensor_board_iteration_callback(store.solution)
        if iteration % dump_interval == 0:
            persist_store(store)
        iteration += 1

    persist_store(store)

    # Final write to tensorboard
    if store.settings.log_to_tensor_board:
        from o2.util.tensorboard_helper import TensorBoardHelper

        TensorBoardHelper.instance.tensor_board_iteration_callback(store.solution, write_everything=True)

    if not store.settings.disable_parallel_evaluation:
        optimizer.executor.shutdown()


def collect_data_sequentially(base_store: Store, args) -> None:
    """Collect all possible solutions and the respective Pareto fronts."""
    info("Setting up Store")
    # Set some global settings
    Settings.SHOW_SIMULATION_ERRORS = True
    Settings.RAISE_SIMULATION_ERRORS = False
    Settings.COST_TYPE = CostType.AVG_WT_AND_PT_PER_TASK_INSTANCE
    Settings.DUMP_DISCARDED_SOLUTIONS = True
    Settings.NUMBER_OF_CASES = args.number_of_cases
    Settings.ARCHIVE_TENSORBOARD_LOGS = args.archive_tensorboard_logs
    Settings.ARCHIVE_SOLUTIONS = True
    Settings.DELETE_LOADED_SOLUTION_ARCHIVES = False
    Settings.OVERWRITE_EXISTING_SOLUTION_ARCHIVES = False
    Settings.MAX_YIELDS_PER_ACTION = (
        args.max_number_of_variations_per_action
        if args.max_number_of_variations_per_action != float("inf")
        else None
    )
    Settings.action_variation_selection = (
        ActionVariationSelection.RANDOM_MAX_VARIANTS_PER_ACTION
        if args.max_number_of_variations_per_action != float("inf")
        else ActionVariationSelection.ALL_RANDOM
    )

    # Optionally archive previous TensorBoard logs
    if (
        base_store.settings.log_to_tensor_board or args.log_to_tensor_board
    ) and Settings.ARCHIVE_TENSORBOARD_LOGS:
        from o2.util.tensorboard_helper import TensorBoardHelper

        TensorBoardHelper.move_logs_to_archive_dir()

    stores_to_run = []

    # Use TABU search
    if "Tabu Search" in args.agents:
        store_name = f"Tabu Search {base_store.name}"
        tabu_store = Store.from_state_and_constraints(
            base_store.base_state,
            base_store.constraints,
            store_name,
        )
        update_store_settings(
            tabu_store,
            AgentType.TABU_SEARCH,
            args.max_iterations,
            args.max_non_improving_actions,
            args.max_threads,
            args.max_number_of_actions_per_iteration or args.max_threads,
            args.log_to_tensor_board,
            args.iterations_per_solution,
        )
        solve_store(tabu_store, args.dump_interval)
        stores_to_run.append(("Tabu Search", tabu_store))
    if "Tabu Search Random" in args.agents:
        store_name = f"Tabu Search Random {base_store.name}"
        tabu_store = Store.from_state_and_constraints(
            base_store.base_state,
            base_store.constraints,
            store_name,
        )
        update_store_settings(
            tabu_store,
            AgentType.TABU_SEARCH_RANDOM,
            args.max_iterations,
            args.max_non_improving_actions,
            args.max_threads,
            args.max_number_of_actions_per_iteration or args.max_threads,
            args.log_to_tensor_board,
            args.iterations_per_solution,
        )
        solve_store(tabu_store, args.dump_interval)
        stores_to_run.append(("Tabu Search Random", tabu_store))

    # Use Simulated Annealing
    if "Simulated Annealing" in args.agents:
        store_name = f"Simulated Annealing {base_store.name}"
        sa_store = Store.from_state_and_constraints(
            base_store.base_state,
            base_store.constraints,
            store_name,
        )
        update_store_settings(
            sa_store,
            AgentType.SIMULATED_ANNEALING,
            args.max_iterations,
            args.max_non_improving_actions,
            args.max_threads,
            args.max_number_of_actions_per_iteration or args.max_threads,
            args.log_to_tensor_board,
            args.iterations_per_solution,
        )
        sa_store.settings.sa_initial_temperature = (
            float(args.sa_initial_temperature) if args.sa_initial_temperature != "auto" else "auto"
        )
        sa_store.settings.sa_cooling_factor = (
            float(args.sa_cooling_factor) if args.sa_cooling_factor != "auto" else "auto"
        )
        solve_store(sa_store, args.dump_interval)
        stores_to_run.append(("Simulated Annealing", sa_store))

    if "Simulated Annealing Random" in args.agents:
        store_name = f"Simulated Annealing Random {base_store.name}"
        sa_store = Store.from_state_and_constraints(
            base_store.base_state,
            base_store.constraints,
            store_name,
        )
        update_store_settings(
            sa_store,
            AgentType.SIMULATED_ANNEALING_RANDOM,
            args.max_iterations,
            args.max_non_improving_actions,
            args.max_threads,
            args.max_number_of_actions_per_iteration or args.max_threads,
            args.log_to_tensor_board,
            args.iterations_per_solution,
        )
        sa_store.settings.sa_initial_temperature = (
            float(args.sa_initial_temperature) if args.sa_initial_temperature != "auto" else "auto"
        )
        sa_store.settings.sa_cooling_factor = (
            float(args.sa_cooling_factor) if args.sa_cooling_factor != "auto" else "auto"
        )
        solve_store(sa_store, args.dump_interval)
        stores_to_run.append(("Simulated Annealing Random", sa_store))

    # Use Proximal Policy Optimization (PPO)
    if "Proximal Policy Optimization" in args.agents:
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
            args.max_number_of_actions_per_iteration or args.max_threads,
            args.log_to_tensor_board,
            args.iterations_per_solution,
        )
        ppo_store.settings.disable_parallel_evaluation = True
        ppo_store.settings.max_threads = 1
        ppo_store.settings.max_number_of_actions_per_iteration = 1
        # Disable distance based selection (so we always find a new base solution)
        ppo_store.settings.max_distance_to_new_base_solution = float("inf")
        ppo_store.settings.error_radius_in_percent = None

        solve_store(ppo_store, args.dump_interval)
        stores_to_run.append(("Proximal Policy Optimization", ppo_store))

    if "Proximal Policy Optimization Random" in args.agents:
        ppo_store = Store.from_state_and_constraints(
            base_store.base_state,
            base_store.constraints,
            f"Proximal Policy Optimization Random {base_store.name}",
        )
        update_store_settings(
            ppo_store,
            AgentType.PROXIMAL_POLICY_OPTIMIZATION_RANDOM,
            args.max_iterations,
            args.max_non_improving_actions,
            args.max_threads,
            args.max_number_of_actions_per_iteration or args.max_threads,
            args.log_to_tensor_board,
            args.iterations_per_solution,
        )
        ppo_store.settings.disable_parallel_evaluation = True
        ppo_store.settings.max_threads = 1
        ppo_store.settings.max_number_of_actions_per_iteration = 1
        # Disable distance based selection (so we always find a new base solution)
        ppo_store.settings.max_distance_to_new_base_solution = float("inf")
        ppo_store.settings.error_radius_in_percent = None

        solve_store(ppo_store, args.dump_interval)
        stores_to_run.append(("Proximal Policy Optimization Random", ppo_store))

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
                timetable_path = f"{scenario_folder}/purchasing_example/purchasing_example.json"
                bpmn_path = f"{scenario_folder}/purchasing_example/purchasing_example.bpmn"
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
        stats("All Done!")
