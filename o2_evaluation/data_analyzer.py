import gc
import glob
import pickle
from collections import defaultdict
from typing import TypedDict

from o2.models.settings import CostType, Settings
from o2.models.solution import Solution
from o2.store import Store
from o2.util.logger import IO_LOG_LEVEL, debug, info, setup_logging, stats, warn
from o2.util.solution_dumper import SolutionDumper
from o2.util.stat_calculation_helper import (
    calculate_averaged_hausdorff_distance,
    calculate_delta_metric,
    calculate_hyperarea,
    calculate_purity,
)


class Metrics(TypedDict):
    """Metrics for the given store."""

    store_name: str
    scenario: str
    agent: str
    mode: str
    number_of_solutions: int
    patreto_size: int
    hyperarea: float
    hyperarea_ratio: float
    hausdorff_distance: float
    delta: float
    purity: float

    base_x: float
    base_y: float

    best_x: float
    best_y: float

    avg_x: float
    avg_y: float

    best_cycle_time: float
    pareto_avg_cycle_time: float
    base_cycle_time: float


EMPTY_METRIC: Metrics = {
    "store_name": "Empty",
    "scenario": "Empty",
    "agent": "Empty",
    "mode": "Empty",
    "number_of_solutions": -1,
    "patreto_size": -1,
    "hyperarea": -1.0,
    "hyperarea_ratio": -1.0,
    "hausdorff_distance": -1.0,
    "delta": -1.0,
    "purity": -1.0,
    "base_x": -1.0,
    "base_y": -1.0,
    "best_x": -1.0,
    "best_y": -1.0,
    "avg_x": -1.0,
    "avg_y": -1.0,
    "best_cycle_time": -1.0,
    "pareto_avg_cycle_time": -1.0,
    "base_cycle_time": -1.0,
}


def calculate_metrics(
    scenario: str,
    mode: str,
    stores: list[tuple[str, Store]],
    extra_solutions: list[Solution] = [],
) -> list[Metrics]:
    """Calculate the metrics for the given stores."""
    info(f"Calculating metrics for {scenario} ({mode})")
    all_solutions: set[Solution] = set()
    for _, store in stores:
        solutions = [
            solution
            for solution in store.solution_tree.solution_lookup.values()
            if solution is not None and solution.is_valid
        ]
        all_solutions.update(solutions)

    all_solutions.update(
        [
            extra_solution
            for extra_solution in extra_solutions
            if extra_solution.is_valid
        ]
    )
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
    debug(f"Calculated reference front with {len(all_solutions_front)} solutions")
    # Calculate the hyperarea (using the max cost and time as the center point)
    max_cost = max(solution.pareto_x for solution in all_solutions)
    max_time = max(solution.pareto_y for solution in all_solutions)
    center_point = (max_cost, max_time)
    global_hyperarea = calculate_hyperarea(all_solutions_front, center_point)

    best_x = min(solution.pareto_x for solution in all_solutions_front)
    best_y = min(solution.pareto_y for solution in all_solutions_front)

    avg_x = sum(solution.pareto_x for solution in all_solutions_front) / len(
        all_solutions_front
    )
    avg_y = sum(solution.pareto_y for solution in all_solutions_front) / len(
        all_solutions_front
    )

    avg_cycle_time = sum(
        solution.evaluation.total_cycle_time for solution in all_solutions_front
    ) / len(all_solutions)

    best_cycle_time = min(
        solution.evaluation.total_cycle_time for solution in all_solutions_front
    )

    base_cycle_time = stores[0][1].base_evaluation.total_cycle_time
    base_x = stores[0][1].base_solution.pareto_x
    base_y = stores[0][1].base_solution.pareto_y

    metrics: list[Metrics] = []

    metrics.append(
        {
            "store_name": f"Global {scenario}",
            "scenario": scenario,
            "agent": "Global",
            "mode": mode,
            "number_of_solutions": len(all_solutions),
            "patreto_size": len(all_solutions_front),
            "hyperarea": global_hyperarea,
            "hyperarea_ratio": -1.0,
            "hausdorff_distance": -1.0,
            "delta": -1.0,
            "purity": -1.0,
            "base_x": base_x,
            "base_y": base_y,
            "best_x": best_x,
            "best_y": best_y,
            "avg_x": avg_x,
            "avg_y": avg_y,
            "best_cycle_time": best_cycle_time,
            "pareto_avg_cycle_time": avg_cycle_time,
            "base_cycle_time": base_cycle_time,
        }
    )

    for name, store in stores:
        agent = get_agent_from_store_name(store.name)
        pareto_solutions = store.current_pareto_front.solutions
        pareto_hyperarea = calculate_hyperarea(pareto_solutions, center_point)
        ratio = 0.0 if global_hyperarea == 0.0 else pareto_hyperarea / global_hyperarea

        hausdorff_distance = calculate_averaged_hausdorff_distance(
            pareto_solutions, all_solutions_front
        )
        delta = calculate_delta_metric(pareto_solutions, all_solutions_front)
        purity = calculate_purity(pareto_solutions, all_solutions_front)

        best_x = store.current_pareto_front.min_x
        best_y = store.current_pareto_front.min_y

        avg_x = sum(solution.pareto_x for solution in pareto_solutions) / len(
            pareto_solutions
        )
        avg_y = sum(solution.pareto_y for solution in pareto_solutions) / len(
            pareto_solutions
        )

        avg_cycle_time = sum(
            solution.evaluation.total_cycle_time for solution in pareto_solutions
        ) / len(pareto_solutions)

        best_cycle_time = min(
            solution.evaluation.total_cycle_time for solution in pareto_solutions
        )

        metrics.append(
            {
                "store_name": store.name,
                "scenario": scenario,
                "agent": agent,
                "mode": mode,
                "number_of_solutions": store.solution_tree.total_solutions,
                "patreto_size": store.current_pareto_front.size,
                "hyperarea": pareto_hyperarea,
                "hyperarea_ratio": ratio,
                "hausdorff_distance": hausdorff_distance,
                "delta": delta,
                "purity": purity,
                "base_x": base_x,
                "base_y": base_y,
                "best_x": best_x,
                "best_y": best_y,
                "avg_x": avg_x,
                "avg_y": avg_y,
                "pareto_avg_cycle_time": avg_cycle_time,
                "base_cycle_time": base_cycle_time,
                "best_cycle_time": best_cycle_time,
            }
        )
        debug(f"Calculated metrics for agent {agent} ({scenario} {mode})")

    return metrics


def get_agent_from_filename(path: str) -> str:
    filename = path.split("/")[-1]
    if not filename.startswith("store_") and not filename.startswith("solutions_"):
        raise ValueError(f"Invalid filename: {filename}")
    if "tabu_search_random" in filename:
        return "Tabu Search Random"
    elif "simulated_annealing_random" in filename:
        return "Simulated Annealing Random"
    elif "tabu_search" in filename:
        return "Tabu Search"
    elif "simulated_annealing" in filename:
        return "Simulated Annealing"
    elif "proximal_policy_optimization" in filename:
        return "Proximal Policy Optimization"
    else:
        raise ValueError(f"Invalid filename: {filename}")


def get_scenario_from_filename(path: str) -> str:
    filename = path.split("/")[-1]
    if not filename.startswith("store_") and not filename.startswith("solutions_"):
        raise ValueError(f"Invalid filename: {path}")
    return (
        filename.replace("store_", "")
        .replace("solutions_", "")
        .replace(".pkl", "")
        .replace("tabu_search_random_", "")
        .replace("simulated_annealing_random_", "")
        .replace("proximal_policy_optimization_random_", "")
        .replace("tabu_search_", "")
        .replace("simulated_annealing_", "")
        .replace("proximal_policy_optimization_", "")
        .replace("global_", "")
        .replace("_", " ")
        .title()
    )


def get_scenario_without_mode(scenario: str) -> str:
    return (
        scenario.lower()
        .replace(" easy", "")
        .replace(" mid", "")
        .replace(" hard", "")
        .title()
    )


def get_mode_from_scenario(scenario: str) -> str:
    scenario = scenario.lower()
    if "global" in scenario:
        return "global"
    elif "_easy" in scenario or " easy" in scenario:
        return "easy"
    elif "_mid" in scenario or " mid" in scenario:
        return "mid"
    elif "_hard" in scenario or " hard" in scenario:
        return "hard"
    else:
        raise ValueError(f"Invalid scenario: {scenario}")


def get_agent_from_store_name(store_name: str) -> str:
    if "tabu search random" in store_name.lower():
        return "Tabu Search Random"
    elif "simulated annealing random" in store_name.lower():
        return "Simulated Annealing Random"
    elif "tabu search" in store_name.lower():
        return "Tabu Search"
    elif "simulated annealing" in store_name.lower():
        return "Simulated Annealing"
    elif "proximal policy optimization" in store_name.lower():
        return "Proximal Policy Optimization"
    else:
        raise ValueError(f"Invalid store name: {store_name}")


def get_scenario_from_store_name(store_name: str) -> str:
    return (
        store_name.lower()
        .replace("tabu search ", "")
        .replace("simulated annealing ", "")
        .replace("proximal policy optimization ", "")
        .replace("global ", "")
        .replace("_global", "")
        .replace("_easy", "")
        .replace("_mid", "")
        .replace("_hard", "")
        .title()
    )


def get_metrics_for_agent(
    metrics: list[Metrics], agent: str
) -> tuple[Metrics, Metrics, Metrics]:
    easy = next(
        (m for m in metrics if m["agent"] == agent and m["mode"] == "easy"),
        EMPTY_METRIC,
    )
    mid = next(
        (m for m in metrics if m["agent"] == agent and m["mode"] == "mid"),
        EMPTY_METRIC,
    )
    hard = next(
        (m for m in metrics if m["agent"] == agent and m["mode"] == "hard"),
        EMPTY_METRIC,
    )
    return easy, mid, hard


def print_metrics_in_google_sheet_format(metrics: list[Metrics]) -> None:
    # Print the metrics in google sheet format
    # For Reference:

    # Group solutions, that have the same scenario (but different _easy, _mid, _hard)
    grouped_metrics = defaultdict(list)
    for metric in metrics:
        grouped_metrics[metric["scenario"]].append(metric)

    result = ""
    for scenario, metrics in grouped_metrics.items():
        result += "----------------------------------------\n"
        result += f"Sheet: {scenario}\n"
        result += "----------------------------------------\n\n"
        result += "Pareto Metrics;;Easy;Mid;Hard\n"
        reference_easy, reference_mid, reference_hard = get_metrics_for_agent(
            metrics, "Global"
        )

        ppo_easy, ppo_mid, ppo_hard = get_metrics_for_agent(
            metrics, "Proximal Policy Optimization"
        )
        sa_easy, sa_mid, sa_hard = get_metrics_for_agent(metrics, "Simulated Annealing")

        tabu_search_easy, tabu_search_mid, tabu_search_hard = get_metrics_for_agent(
            metrics, "Tabu Search"
        )

        tabu_search_random_easy, tabu_search_random_mid, tabu_search_random_hard = (
            get_metrics_for_agent(metrics, "Tabu Search Random")
        )
        (
            simulated_annealing_random_easy,
            simulated_annealing_random_mid,
            simulated_annealing_random_hard,
        ) = get_metrics_for_agent(metrics, "Simulated Annealing Random")

        result += "# Solutions\n"
        result += f";Total Unique;{reference_easy['number_of_solutions']};{reference_mid['number_of_solutions']};{reference_hard['number_of_solutions']}\n"
        result += f";SA;{sa_easy['number_of_solutions']};{sa_mid['number_of_solutions']};{sa_hard['number_of_solutions']}\n"
        result += f";Tabu Search;{tabu_search_easy['number_of_solutions']};{tabu_search_mid['number_of_solutions']};{tabu_search_hard['number_of_solutions']}\n"
        result += f";PPO;{ppo_easy['number_of_solutions']};{ppo_mid['number_of_solutions']};{ppo_hard['number_of_solutions']}\n"
        result += f";Tabu Random;{tabu_search_random_easy['number_of_solutions']};{tabu_search_random_mid['number_of_solutions']};{tabu_search_random_hard['number_of_solutions']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['number_of_solutions']};{simulated_annealing_random_mid['number_of_solutions']};{simulated_annealing_random_hard['number_of_solutions']}\n\n"

        result += "Pareto Size\n"
        result += f";Reference;{reference_easy['patreto_size']};{reference_mid['patreto_size']};{reference_hard['patreto_size']}\n"
        result += f";SA;{sa_easy['patreto_size']};{sa_mid['patreto_size']};{sa_hard['patreto_size']}\n"
        result += f";Tabu Search;{tabu_search_easy['patreto_size']};{tabu_search_mid['patreto_size']};{tabu_search_hard['patreto_size']}\n"
        result += f";PPO;{ppo_easy['patreto_size']};{ppo_mid['patreto_size']};{ppo_hard['patreto_size']}\n"
        result += f";Tabu Random;{tabu_search_random_easy['patreto_size']};{tabu_search_random_mid['patreto_size']};{tabu_search_random_hard['patreto_size']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['patreto_size']};{simulated_annealing_random_mid['patreto_size']};{simulated_annealing_random_hard['patreto_size']}\n\n"

        result += "Hyperarea Ratio\n"
        result += f";SA;{sa_easy['hyperarea_ratio']};{sa_mid['hyperarea_ratio']};{sa_hard['hyperarea_ratio']}\n"
        result += f";Tabu Search;{tabu_search_easy['hyperarea_ratio']};{tabu_search_mid['hyperarea_ratio']};{tabu_search_hard['hyperarea_ratio']}\n"
        result += f";PPO;{ppo_easy['hyperarea_ratio']};{ppo_mid['hyperarea_ratio']};{ppo_hard['hyperarea_ratio']}\n"
        result += f";Tabu Random;{tabu_search_random_easy['hyperarea_ratio']};{tabu_search_random_mid['hyperarea_ratio']};{tabu_search_random_hard['hyperarea_ratio']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['hyperarea_ratio']};{simulated_annealing_random_mid['hyperarea_ratio']};{simulated_annealing_random_hard['hyperarea_ratio']}\n\n"

        result += "Hausdorff\n"
        result += f";SA;{sa_easy['hausdorff_distance']};{sa_mid['hausdorff_distance']};{sa_hard['hausdorff_distance']}\n"
        result += f";Tabu Search;{tabu_search_easy['hausdorff_distance']};{tabu_search_mid['hausdorff_distance']};{tabu_search_hard['hausdorff_distance']}\n"
        result += f";PPO;{ppo_easy['hausdorff_distance']};{ppo_mid['hausdorff_distance']};{ppo_hard['hausdorff_distance']}\n"
        result += f";Tabu Random;{tabu_search_random_easy['hausdorff_distance']};{tabu_search_random_mid['hausdorff_distance']};{tabu_search_random_hard['hausdorff_distance']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['hausdorff_distance']};{simulated_annealing_random_mid['hausdorff_distance']};{simulated_annealing_random_hard['hausdorff_distance']}\n\n"

        result += "Delta\n"
        result += f";SA;{sa_easy['delta']};{sa_mid['delta']};{sa_hard['delta']}\n"
        result += f";Tabu Search;{tabu_search_easy['delta']};{tabu_search_mid['delta']};{tabu_search_hard['delta']}\n"
        result += f";PPO;{ppo_easy['delta']};{ppo_mid['delta']};{ppo_hard['delta']}\n"
        result += f";Tabu Random;{tabu_search_random_easy['delta']};{tabu_search_random_mid['delta']};{tabu_search_random_hard['delta']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['delta']};{simulated_annealing_random_mid['delta']};{simulated_annealing_random_hard['delta']}\n\n"

        result += "Purity\n"
        result += f";SA;{sa_easy['purity']};{sa_mid['purity']};{sa_hard['purity']}\n"
        result += f";Tabu Search;{tabu_search_easy['purity']};{tabu_search_mid['purity']};{tabu_search_hard['purity']}\n"
        result += (
            f";PPO;{ppo_easy['purity']};{ppo_mid['purity']};{ppo_hard['purity']}\n"
        )
        result += f";Tabu Random;{tabu_search_random_easy['purity']};{tabu_search_random_mid['purity']};{tabu_search_random_hard['purity']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['purity']};{simulated_annealing_random_mid['purity']};{simulated_annealing_random_hard['purity']}\n\n"

        result += "Avg Cycle Time\n"
        result += f";Base;{reference_easy['base_cycle_time']};{reference_mid['base_cycle_time']};{reference_hard['base_cycle_time']}\n"
        result += f";Reference;{reference_easy['pareto_avg_cycle_time']};{reference_mid['pareto_avg_cycle_time']};{reference_hard['pareto_avg_cycle_time']}\n"
        result += f";SA;{sa_easy['pareto_avg_cycle_time']};{sa_mid['pareto_avg_cycle_time']};{sa_hard['pareto_avg_cycle_time']}\n"
        result += f";Tabu Search;{tabu_search_easy['pareto_avg_cycle_time']};{tabu_search_mid['pareto_avg_cycle_time']};{tabu_search_hard['pareto_avg_cycle_time']}\n"
        result += f";PPO;{ppo_easy['pareto_avg_cycle_time']};{ppo_mid['pareto_avg_cycle_time']};{ppo_hard['pareto_avg_cycle_time']}\n"
        result += f";Tabu Random;{tabu_search_random_easy['pareto_avg_cycle_time']};{tabu_search_random_mid['pareto_avg_cycle_time']};{tabu_search_random_hard['pareto_avg_cycle_time']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['pareto_avg_cycle_time']};{simulated_annealing_random_mid['pareto_avg_cycle_time']};{simulated_annealing_random_hard['pareto_avg_cycle_time']}\n\n"

        result += "Best Cycle Time\n"
        result += f";Base;{reference_easy['base_cycle_time']};{reference_mid['base_cycle_time']};{reference_hard['base_cycle_time']}\n"
        result += f";Reference;{reference_easy['best_cycle_time']};{reference_mid['best_cycle_time']};{reference_hard['best_cycle_time']}\n"
        result += f";SA;{sa_easy['best_cycle_time']};{sa_mid['best_cycle_time']};{sa_hard['best_cycle_time']}\n"
        result += f";Tabu Search;{tabu_search_easy['best_cycle_time']};{tabu_search_mid['best_cycle_time']};{tabu_search_hard['best_cycle_time']}\n"
        result += f";PPO;{ppo_easy['best_cycle_time']};{ppo_mid['best_cycle_time']};{ppo_hard['best_cycle_time']}\n"
        result += f";Tabu Random;{tabu_search_random_easy['best_cycle_time']};{tabu_search_random_mid['best_cycle_time']};{tabu_search_random_hard['best_cycle_time']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['best_cycle_time']};{simulated_annealing_random_mid['best_cycle_time']};{simulated_annealing_random_hard['best_cycle_time']}\n\n"

        result += f"Best {Settings.get_pareto_x_label()}\n"
        result += f";Base;{reference_easy['base_x']};{reference_mid['base_x']};{reference_hard['base_x']}\n"
        result += f";Reference;{reference_easy['best_x']};{reference_mid['best_x']};{reference_hard['best_x']}\n"
        result += f";SA;{sa_easy['best_x']};{sa_mid['best_x']};{sa_hard['best_x']}\n"
        result += f";Tabu Search;{tabu_search_easy['best_x']};{tabu_search_mid['best_x']};{tabu_search_hard['best_x']}\n"
        result += (
            f";PPO;{ppo_easy['best_x']};{ppo_mid['best_x']};{ppo_hard['best_x']}\n"
        )
        result += f";Tabu Random;{tabu_search_random_easy['best_x']};{tabu_search_random_mid['best_x']};{tabu_search_random_hard['best_x']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['best_x']};{simulated_annealing_random_mid['best_x']};{simulated_annealing_random_hard['best_x']}\n\n"

        result += f"Best {Settings.get_pareto_y_label()}\n"
        result += f";Base;{reference_easy['base_y']};{reference_mid['base_y']};{reference_hard['base_y']}\n"
        result += f";Reference;{reference_easy['best_y']};{reference_mid['best_y']};{reference_hard['best_y']}\n"
        result += f";SA;{sa_easy['best_y']};{sa_mid['best_y']};{sa_hard['best_y']}\n"
        result += f";Tabu Search;{tabu_search_easy['best_y']};{tabu_search_mid['best_y']};{tabu_search_hard['best_y']}\n"
        result += (
            f";PPO;{ppo_easy['best_y']};{ppo_mid['best_y']};{ppo_hard['best_y']}\n"
        )
        result += f";Tabu Random;{tabu_search_random_easy['best_y']};{tabu_search_random_mid['best_y']};{tabu_search_random_hard['best_y']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['best_y']};{simulated_annealing_random_mid['best_y']};{simulated_annealing_random_hard['best_y']}\n\n"

        result += f"Avg {Settings.get_pareto_x_label()}\n"
        result += f";Base;{reference_easy['base_x']};{reference_mid['base_x']};{reference_hard['base_x']}\n"
        result += f";Reference;{reference_easy['avg_x']};{reference_mid['avg_x']};{reference_hard['avg_x']}\n"
        result += f";SA;{sa_easy['avg_x']};{sa_mid['avg_x']};{sa_hard['avg_x']}\n"
        result += f";Tabu Search;{tabu_search_easy['avg_x']};{tabu_search_mid['avg_x']};{tabu_search_hard['avg_x']}\n"
        result += f";PPO;{ppo_easy['avg_x']};{ppo_mid['avg_x']};{ppo_hard['avg_x']}\n"

        result += f"Avg {Settings.get_pareto_y_label()}\n"
        result += f";Base;{reference_easy['base_y']};{reference_mid['base_y']};{reference_hard['base_y']}\n"
        result += f";Reference;{reference_easy['avg_y']};{reference_mid['avg_y']};{reference_hard['avg_y']}\n"
        result += f";SA;{sa_easy['avg_y']};{sa_mid['avg_y']};{sa_hard['avg_y']}\n"
        result += f";Tabu Search;{tabu_search_easy['avg_y']};{tabu_search_mid['avg_y']};{tabu_search_hard['avg_y']}\n"
        result += f";PPO;{ppo_easy['avg_y']};{ppo_mid['avg_y']};{ppo_hard['avg_y']}\n"

    print(result.replace(".", ","))


if __name__ == "__main__":
    Settings.LOG_LEVEL = "IO"
    Settings.LOG_FILE = "logs/data_analyzer.log"
    Settings.COST_TYPE = CostType.AVG_WT_AND_PT_PER_TASK_INSTANCE
    Settings.ARCHIVE_SOLUTIONS = True
    Settings.DELETE_LOADED_SOLUTION_ARCHIVES = False
    Settings.OVERWRITE_EXISTING_SOLUTION_ARCHIVES = False
    Settings.CHECK_FOR_TIMETABLE_EQUALITY = True
    setup_logging()

    SolutionDumper(analysis_mode=True)

    gc.disable()
    # Get the redumped stores for better performance
    analyze_stores_dir = "o2_evaluation/redumped_stores"
    # Get the solutions for the old analyze_stores folder
    analyze_solutions_dir = "o2_evaluation/redumped_stores"
    analyze_stores_file_list = glob.glob(f"{analyze_stores_dir}/**store_*.pkl")
    solution_files_list = glob.glob(f"{analyze_solutions_dir}/**solutions_*.pkl")
    # Scenario, Model, Store
    stores_files: defaultdict[str, list[str]] = defaultdict(list)
    solutions_files: defaultdict[str, list[str]] = defaultdict(list)

    for file in analyze_stores_file_list:
        stores_files[get_scenario_from_filename(file)].append(file)

    for file in solution_files_list:
        solutions_files[get_scenario_from_filename(file)].append(file)

    scenarios = list(stores_files.keys())
    all_metrics: list[Metrics] = []

    for scenario in scenarios:
        if not "Bpi Challenge 2012" in scenario:
            continue
        mode = get_mode_from_scenario(scenario)
        scenario_without_mode = get_scenario_without_mode(scenario)

        stats(f"Processing scenario: {scenario_without_mode} ({mode})")
        stores: list[tuple[str, Store]] = []
        solutions: list[Solution] = []
        for file in stores_files[scenario]:
            debug(
                f"Loading store from {file}... ({get_scenario_from_filename(file)}, {get_agent_from_filename(file)})"
            )
            with open(file, "rb") as f:
                try:
                    store = pickle.load(f)
                    stores.append(
                        (
                            get_agent_from_filename(file),
                            store,
                        )
                    )
                    debug(f"Loaded store '{store.name}' from {file}")
                except Exception as e:
                    warn(f"Error loading store from {file}: {e}")

        for file in solutions_files[scenario]:
            with open(file, "rb") as f:
                debug(f"Loading solutions from {file}...")
                while True:
                    try:
                        solution = pickle.load(f)
                        solutions.append(solution)
                    except EOFError:
                        break
                    except Exception as e:
                        warn(f"Error loading (more) solutions from {file}: {e}")
                        break
                debug(f"Loaded solutions from {file}")

        info(f"Loaded {len(stores)} stores and {len(solutions)} solutions")

        # Calculate the metrics for the given stores
        metrics = calculate_metrics(
            scenario_without_mode,
            mode,
            stores,
            solutions,
        )

        all_metrics.extend(metrics)

    pickle.dump(all_metrics, open("all_metrics.pkl", "wb"))
    # Print the metrics in google sheet format
    print_metrics_in_google_sheet_format(all_metrics)
