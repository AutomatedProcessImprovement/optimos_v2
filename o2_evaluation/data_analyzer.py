import gc
import glob
import pickle
from collections import defaultdict
from collections.abc import Iterable
from typing import Optional, TypedDict

from o2.models.evaluation import Evaluation
from o2.models.settings import CostType, Settings
from o2.models.solution import Solution
from o2.store import Store
from o2.util.logger import debug, info, setup_logging, stats, warn
from o2.util.solution_dumper import SolutionDumper
from o2.util.stat_calculation_helper import (
    calculate_averaged_hausdorff_distance,
    calculate_delta_metric,
    calculate_hyperarea,
    calculate_purity,
)

INCLUDE_SOLUTIONS_WITHOUT_STORE = True


class Metrics(TypedDict):
    """Metrics for the given store."""

    store_name: str
    scenario: str
    agent: str
    mode: str

    iterations: int

    number_of_solutions: int
    invalid_solutions: int
    invalid_solutions_ratio: float
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
    best_avg_cycle_time: float
    base_avg_cycle_time: float


EMPTY_METRIC: Metrics = {
    "store_name": "Empty",
    "scenario": "Empty",
    "agent": "Empty",
    "mode": "Empty",
    "iterations": -1,
    "number_of_solutions": -1,
    "invalid_solutions": -1,
    "invalid_solutions_ratio": -1.0,
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
    "best_avg_cycle_time": -1.0,
    "base_avg_cycle_time": -1.0,
}


def create_front_from_solutions(solutions: Iterable[Solution]) -> list[Solution]:
    """Create the Pareto front from the given solutions."""
    return list(
        set(
            solution
            for solution in solutions
            if solution.is_valid
            and not any(
                solution.is_dominated_by(other)
                for other in solutions
                if other.is_valid and other.point != solution.point
            )
        )
    )


def filter_solutions(
    solutions: Iterable[Solution],
    name: Optional[str] = None,
    not_name: Optional[str] = None,
    valid: bool = True,
) -> list[Solution]:
    """Filter the solutions based on the name and validity."""
    return [
        solution
        for solution in solutions
        if (name is None or name.lower() in solution.__dict__["_store_name"].lower())
        and (not_name is None or not_name.lower() not in solution.__dict__["_store_name"].lower())
        and solution.is_valid == valid
    ]


def filter_solution_ids(
    solutions: Iterable[Solution],
    name: Optional[str] = None,
    not_name: Optional[str] = None,
    valid: bool = True,
) -> list[str]:
    """Filter the solution ids based on the name and validity."""
    return [solution.id for solution in filter_solutions(solutions, name, not_name, valid)]


def _update_evaluation(solution: Solution, evaluation: Evaluation) -> None:
    solution.__dict__["evaluation"] = None
    solution.__dict__["_evaluation"] = evaluation
    solution.__dict__["pareto_x"] = evaluation.pareto_x
    solution.__dict__["pareto_y"] = evaluation.pareto_y
    solution.__dict__["point"] = (evaluation.pareto_x, evaluation.pareto_y)
    solution.__dict__["is_valid"] = not evaluation.is_empty


def handle_duplicates(solutions: Iterable[Solution]) -> None:
    """Handle duplicate solutions by updating the evaluation of the duplicate solution."""
    duplicate_lookup: dict[int, Solution] = {}
    for solution in solutions:
        if not solution.is_valid:
            continue
        if duplicate_lookup.get(hash(solution)) is None:
            duplicate_lookup[hash(solution)] = solution
        else:
            try:
                first_solution = duplicate_lookup[hash(solution)]
                first_evaluation = first_solution.evaluation
                second_evaluation = solution.evaluation
            except Exception as e:
                warn(f"Error getting evaluation for {solution.id}: {e}")
                continue
            if not first_solution.is_valid and not solution.is_valid:
                warn(f"Duplicate solution found: {solution.id}, both are invalid!")
                continue
            elif solution.is_valid and first_evaluation.total_cycle_time > second_evaluation.total_cycle_time:
                _update_evaluation(first_solution, second_evaluation)
                duplicate_lookup[hash(solution)] = solution
                # log_io(f"Duplicate solution found: {solution.id}, keeping it.")
            else:
                # log_io(f"Duplicate solution found: {solution.id}, keeping first ({first_solution.id}).")
                _update_evaluation(solution, first_evaluation)


def recalculate_pareto_front(solution_dict: dict[str, Solution], store: Store) -> list[Solution]:
    """Recalculate the Pareto front for the given store."""
    store_solutions: list[Solution] = []
    for solution_id in store.solution_tree.solution_lookup:
        solution = store.solution_tree.solution_lookup.get(solution_id) or solution_dict.get(solution_id)
        if solution is not None and solution.is_valid:
            solution.__dict__["_store_name"] = store.name
            store_solutions.append(solution)
        elif solution is None:
            warn(f"Solution {solution_id} not found in store {store.name}!")

    if INCLUDE_SOLUTIONS_WITHOUT_STORE:
        for solution in solution_dict.values():
            if (
                solution is not None
                and solution.is_valid
                and solution.__dict__["_store_name"] == store.name
                and solution.id not in store.solution_tree.solution_lookup
            ):
                store_solutions.append(solution)

    return create_front_from_solutions(store_solutions)


def calculate_metrics(
    scenario: str,
    mode: str,
    stores: list[tuple[str, Store]],
    extra_solutions: list[Solution] = [],
) -> list[Metrics]:
    """Calculate the metrics for the given stores."""
    info(f"Calculating metrics for {scenario} ({mode})")

    extra_solutions_dict: dict[str, Solution] = {solution.id: solution for solution in extra_solutions}
    added_extra_solutions: set[tuple[str, str]] = set()

    all_solutions_list: list[Solution] = list()
    all_invalid_solutions: set[str] = set()
    random_invalid_solutions: set[str] = set()
    optimos_invalid_solutions: set[str] = set()

    def handle_invalid_solution(solution_id: str, solution: Solution) -> None:
        all_invalid_solutions.add(solution_id)
        if "random" in store.name.lower():
            random_invalid_solutions.add(solution_id)
        else:
            optimos_invalid_solutions.add(solution_id)
        if solution is not None:
            all_solutions_list.append(solution)

    for _, store in stores:
        for solution_id, solution in store.solution_tree.solution_lookup.items():
            if solution is not None and solution.is_valid:
                # Add store name so we can load the evaluation and state later
                solution.__dict__["_store_name"] = store.name
                all_solutions_list.append(solution)
            elif solution is not None and not solution.is_valid:
                handle_invalid_solution(solution_id, solution)
            elif extra_solutions_dict.get(solution_id) is not None:
                added_extra_solutions.add((store.name, solution_id))
                if extra_solutions_dict[solution_id].is_valid:
                    all_solutions_list.append(extra_solutions_dict[solution_id])
                else:
                    handle_invalid_solution(solution_id, extra_solutions_dict[solution_id])
            else:
                warn(f"Solution {solution_id} of {store.name} not found in store or extra solutions!")
        for pareto in store.pareto_fronts:
            for solution in pareto.solutions:
                if solution is not None and solution.is_valid:
                    # Add store name so we can load the evaluation and state later
                    solution.__dict__["_store_name"] = store.name
                    all_solutions_list.append(solution)
                elif solution is not None and not solution.is_valid:
                    handle_invalid_solution(solution.id, solution)

    if INCLUDE_SOLUTIONS_WITHOUT_STORE:
        for solution in extra_solutions:
            if (solution.__dict__["_store_name"], solution.id) not in added_extra_solutions:
                if solution is not None and solution.is_valid:
                    all_solutions_list.append(solution)
                elif solution is not None and not solution.is_valid:  # noqa: SIM102
                    handle_invalid_solution(solution.id, solution)

    handle_duplicates(all_solutions_list)

    all_solutions_dict: dict[str, Solution] = {solution.id: solution for solution in all_solutions_list}

    all_valid_solutions = set(filter_solutions(all_solutions_list, valid=True))

    random_solutions: set[Solution] = set(filter_solutions(all_valid_solutions, name="random", valid=True))
    optimos_solutions: set[Solution] = set(
        filter_solutions(all_valid_solutions, not_name="random", valid=True)
    )

    # Find the Pareto front (non-dominated solutions)
    all_solutions_front = create_front_from_solutions(all_valid_solutions)
    random_solutions_front = create_front_from_solutions(random_solutions)
    optimos_solutions_front = create_front_from_solutions(optimos_solutions)

    debug(f"Calculated reference fronts with {len(all_solutions_front)} solutions")
    # Calculate the hyperarea (using the max cost and time as the center point)
    max_cost = max(solution.pareto_x for solution in all_valid_solutions)
    max_time = max(solution.pareto_y for solution in all_valid_solutions)
    center_point = (max_cost, max_time)
    global_hyperarea = calculate_hyperarea(all_solutions_front, center_point)

    base_cycle_time = stores[0][1].base_evaluation.total_cycle_time
    base_avg_cycle_time = stores[0][1].base_evaluation.avg_cycle_time_by_case
    base_x = stores[0][1].base_solution.pareto_x
    base_y = stores[0][1].base_solution.pareto_y

    def create_reference_metrics(
        agent: str,
        scenario: str,
        mode: str,
        front: list[Solution],
        center_point: tuple[float, float],
        no_of_solutions: int,
        no_of_invalid_solutions: int,
    ) -> Metrics:
        pareto_hyperarea = calculate_hyperarea(front, center_point)
        ratio = 0.0 if global_hyperarea == 0.0 else pareto_hyperarea / global_hyperarea

        hausdorff_distance = calculate_averaged_hausdorff_distance(front, all_solutions_front)
        delta = calculate_delta_metric(front, all_solutions_front)
        purity = calculate_purity(front, all_solutions_front)

        best_x = min(solution.pareto_x for solution in front)
        best_y = min(solution.pareto_y for solution in front)

        avg_x = sum(solution.pareto_x for solution in front) / len(front)
        avg_y = sum(solution.pareto_y for solution in front) / len(front)

        avg_cycle_time = sum(solution.evaluation.total_cycle_time for solution in front) / len(front)

        best_cycle_time = min(solution.evaluation.total_cycle_time for solution in front)

        best_avg_cycle_time = min(solution.evaluation.avg_cycle_time_by_case for solution in front)

        return {
            "store_name": f"{agent} {scenario}",
            "scenario": scenario,
            "agent": agent,
            "mode": mode,
            "iterations": -1,
            "number_of_solutions": no_of_solutions,
            "invalid_solutions": no_of_invalid_solutions,
            "invalid_solutions_ratio": no_of_invalid_solutions / no_of_solutions,
            "patreto_size": len(front),
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
            "base_avg_cycle_time": base_avg_cycle_time,
            "best_avg_cycle_time": best_avg_cycle_time,
        }

    metrics: list[Metrics] = []

    metrics.append(
        {
            "store_name": f"Global {scenario}",
            "scenario": scenario,
            "agent": "Global",
            "mode": mode,
            "iterations": -1,
            "number_of_solutions": len(all_valid_solutions),
            "invalid_solutions": len(all_invalid_solutions),
            "invalid_solutions_ratio": len(all_invalid_solutions) / len(all_valid_solutions),
            "patreto_size": len(all_solutions_front),
            "hyperarea": global_hyperarea,
            "hyperarea_ratio": -1.0,
            "hausdorff_distance": -1.0,
            "delta": -1.0,
            "purity": -1.0,
            "base_x": base_x,
            "base_y": base_y,
            "best_x": min(solution.pareto_x for solution in all_solutions_front),
            "best_y": min(solution.pareto_y for solution in all_solutions_front),
            "avg_x": sum(solution.pareto_x for solution in all_solutions_front) / len(all_solutions_front),
            "avg_y": sum(solution.pareto_y for solution in all_solutions_front) / len(all_solutions_front),
            "best_cycle_time": min(solution.evaluation.total_cycle_time for solution in all_solutions_front),
            "pareto_avg_cycle_time": sum(
                solution.evaluation.total_cycle_time for solution in all_solutions_front
            )
            / len(all_solutions_front),
            "base_cycle_time": base_cycle_time,
            "base_avg_cycle_time": base_avg_cycle_time,
            "best_avg_cycle_time": min(
                solution.evaluation.avg_cycle_time_by_case for solution in all_solutions_front
            ),
        }
    )

    metrics.append(
        create_reference_metrics(
            "Reference (Random)",
            scenario,
            mode,
            random_solutions_front,
            center_point,
            len(random_solutions),
            len(random_invalid_solutions),
        )
    )

    metrics.append(
        create_reference_metrics(
            "Reference (Optimos)",
            scenario,
            mode,
            optimos_solutions_front,
            center_point,
            len(optimos_solutions),
            len(optimos_invalid_solutions),
        )
    )

    for agent, store in stores:
        info(f"Calculating metrics for {agent} ({scenario} {mode})...")
        number_of_solutions = store.solution_tree.total_solutions
        invalid_solutions = store.solution_tree.discarded_solutions
        invalid_solutions_ratio = invalid_solutions / number_of_solutions
        pareto_solutions = recalculate_pareto_front(all_solutions_dict, store)

        pareto_hyperarea = calculate_hyperarea(pareto_solutions, center_point)
        ratio = 0.0 if global_hyperarea == 0.0 else pareto_hyperarea / global_hyperarea

        hausdorff_distance = calculate_averaged_hausdorff_distance(pareto_solutions, all_solutions_front)
        delta = calculate_delta_metric(pareto_solutions, all_solutions_front)
        purity = calculate_purity(pareto_solutions, all_solutions_front)

        best_x = store.current_pareto_front.min_x
        best_y = store.current_pareto_front.min_y

        avg_x = sum(solution.pareto_x for solution in pareto_solutions) / len(pareto_solutions)
        avg_y = sum(solution.pareto_y for solution in pareto_solutions) / len(pareto_solutions)

        avg_cycle_time = sum(solution.evaluation.total_cycle_time for solution in pareto_solutions) / len(
            pareto_solutions
        )

        best_cycle_time = min(solution.evaluation.total_cycle_time for solution in pareto_solutions)
        best_avg_cycle_time = min(solution.evaluation.avg_cycle_time_by_case for solution in pareto_solutions)

        metrics.append(
            {
                "store_name": store.name,
                "scenario": scenario,
                "agent": agent,
                "mode": mode,
                "iterations": store.__dict__.get("_iteration", -1),
                "number_of_solutions": number_of_solutions,
                "invalid_solutions": invalid_solutions,
                "invalid_solutions_ratio": invalid_solutions_ratio,
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
                "base_avg_cycle_time": base_avg_cycle_time,
                "best_avg_cycle_time": best_avg_cycle_time,
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
    elif "proximal_policy_optimization_random" in filename:
        return "Proximal Policy Optimization Random"
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
    return scenario.lower().replace(" easy", "").replace(" mid", "").replace(" hard", "").title()


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
    elif "proximal policy optimization random" in store_name.lower():
        return "Proximal Policy Optimization Random"
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


def get_metrics_for_agent(metrics: list[Metrics], agent: str) -> tuple[Metrics, Metrics, Metrics]:
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
    """Print the metrics in google sheet format."""
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
        reference_easy, reference_mid, reference_hard = get_metrics_for_agent(metrics, "Global")
        reference_random_easy, reference_random_mid, reference_random_hard = get_metrics_for_agent(
            metrics, "Reference (Random)"
        )
        reference_optimos_easy, reference_optimos_mid, reference_optimos_hard = get_metrics_for_agent(
            metrics, "Reference (Optimos)"
        )

        ppo_easy, ppo_mid, ppo_hard = get_metrics_for_agent(metrics, "Proximal Policy Optimization")
        sa_easy, sa_mid, sa_hard = get_metrics_for_agent(metrics, "Simulated Annealing")

        tabu_search_easy, tabu_search_mid, tabu_search_hard = get_metrics_for_agent(metrics, "Tabu Search")

        tabu_search_random_easy, tabu_search_random_mid, tabu_search_random_hard = get_metrics_for_agent(
            metrics, "Tabu Search Random"
        )
        (
            simulated_annealing_random_easy,
            simulated_annealing_random_mid,
            simulated_annealing_random_hard,
        ) = get_metrics_for_agent(metrics, "Simulated Annealing Random")

        (ppo_random_easy, ppo_random_mid, ppo_random_hard) = get_metrics_for_agent(
            metrics, "Proximal Policy Optimization Random"
        )

        result += "# Iterations\n"
        result += f";SA;{sa_easy['iterations']};{sa_mid['iterations']};{sa_hard['iterations']}\n"
        result += f";Tabu Search;{tabu_search_easy['iterations']};{tabu_search_mid['iterations']};{tabu_search_hard['iterations']}\n"
        result += f";PPO;{ppo_easy['iterations']};{ppo_mid['iterations']};{ppo_hard['iterations']}\n"
        result += f";Tabu Search Random;{tabu_search_random_easy['iterations']};{tabu_search_random_mid['iterations']};{tabu_search_random_hard['iterations']}\n"
        result += f";Simulated Annealing Random;{simulated_annealing_random_easy['iterations']};{simulated_annealing_random_mid['iterations']};{simulated_annealing_random_hard['iterations']}\n"
        result += f";PPO Random;{ppo_random_easy['iterations']};{ppo_random_mid['iterations']};{ppo_random_hard['iterations']}\n\n"

        result += "# Solutions\n"
        result += f";Total Unique;{reference_easy['number_of_solutions']};{reference_mid['number_of_solutions']};{reference_hard['number_of_solutions']}\n"
        result += f";Total Unique Random;{reference_random_easy['number_of_solutions']};{reference_random_mid['number_of_solutions']};{reference_random_hard['number_of_solutions']}\n"
        result += f";Total Unique Optimos;{reference_optimos_easy['number_of_solutions']};{reference_optimos_mid['number_of_solutions']};{reference_optimos_hard['number_of_solutions']}\n"
        result += f";SA;{sa_easy['number_of_solutions']};{sa_mid['number_of_solutions']};{sa_hard['number_of_solutions']}\n"
        result += f";Tabu Search;{tabu_search_easy['number_of_solutions']};{tabu_search_mid['number_of_solutions']};{tabu_search_hard['number_of_solutions']}\n"
        result += f";PPO;{ppo_easy['number_of_solutions']};{ppo_mid['number_of_solutions']};{ppo_hard['number_of_solutions']}\n"
        result += f";Tabu Random;{tabu_search_random_easy['number_of_solutions']};{tabu_search_random_mid['number_of_solutions']};{tabu_search_random_hard['number_of_solutions']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['number_of_solutions']};{simulated_annealing_random_mid['number_of_solutions']};{simulated_annealing_random_hard['number_of_solutions']}\n"
        result += f";PPO Random;{ppo_random_easy['number_of_solutions']};{ppo_random_mid['number_of_solutions']};{ppo_random_hard['number_of_solutions']}\n\n"

        result += "# Invalid Solutions Ratio\n"
        result += f";Total;{reference_easy['invalid_solutions_ratio']};{reference_mid['invalid_solutions_ratio']};{reference_hard['invalid_solutions_ratio']}\n"
        result += f";Total Random;{reference_random_easy['invalid_solutions_ratio']};{reference_random_mid['invalid_solutions_ratio']};{reference_random_hard['invalid_solutions_ratio']}\n"
        result += f";Total Optimos;{reference_optimos_easy['invalid_solutions_ratio']};{reference_optimos_mid['invalid_solutions_ratio']};{reference_optimos_hard['invalid_solutions_ratio']}\n"
        result += f";SA;{sa_easy['invalid_solutions_ratio']};{sa_mid['invalid_solutions_ratio']};{sa_hard['invalid_solutions_ratio']}\n"
        result += f";Tabu Search;{tabu_search_easy['invalid_solutions_ratio']};{tabu_search_mid['invalid_solutions_ratio']};{tabu_search_hard['invalid_solutions_ratio']}\n"
        result += f";PPO;{ppo_easy['invalid_solutions_ratio']};{ppo_mid['invalid_solutions_ratio']};{ppo_hard['invalid_solutions_ratio']}\n"
        result += f";Tabu Random;{tabu_search_random_easy['invalid_solutions_ratio']};{tabu_search_random_mid['invalid_solutions_ratio']};{tabu_search_random_hard['invalid_solutions_ratio']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['invalid_solutions_ratio']};{simulated_annealing_random_mid['invalid_solutions_ratio']};{simulated_annealing_random_hard['invalid_solutions_ratio']}\n"
        result += f";PPO Random;{ppo_random_easy['invalid_solutions_ratio']};{ppo_random_mid['invalid_solutions_ratio']};{ppo_random_hard['invalid_solutions_ratio']}\n\n"

        result += "Pareto Size\n"
        result += f";Reference;{reference_easy['patreto_size']};{reference_mid['patreto_size']};{reference_hard['patreto_size']}\n"
        result += f";Reference Random;{reference_random_easy['patreto_size']};{reference_random_mid['patreto_size']};{reference_random_hard['patreto_size']}\n"
        result += f";Reference Optimos;{reference_optimos_easy['patreto_size']};{reference_optimos_mid['patreto_size']};{reference_optimos_hard['patreto_size']}\n"
        result += f";SA;{sa_easy['patreto_size']};{sa_mid['patreto_size']};{sa_hard['patreto_size']}\n"
        result += f";Tabu Search;{tabu_search_easy['patreto_size']};{tabu_search_mid['patreto_size']};{tabu_search_hard['patreto_size']}\n"
        result += f";PPO;{ppo_easy['patreto_size']};{ppo_mid['patreto_size']};{ppo_hard['patreto_size']}\n"
        result += f";Tabu Random;{tabu_search_random_easy['patreto_size']};{tabu_search_random_mid['patreto_size']};{tabu_search_random_hard['patreto_size']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['patreto_size']};{simulated_annealing_random_mid['patreto_size']};{simulated_annealing_random_hard['patreto_size']}\n"
        result += f";PPO Random;{ppo_random_easy['patreto_size']};{ppo_random_mid['patreto_size']};{ppo_random_hard['patreto_size']}\n\n"

        result += "Hyperarea Ratio\n"
        result += f";Reference Random;{reference_random_easy['hyperarea_ratio']};{reference_random_mid['hyperarea_ratio']};{reference_random_hard['hyperarea_ratio']}\n"
        result += f";Reference Optimos;{reference_optimos_easy['hyperarea_ratio']};{reference_optimos_mid['hyperarea_ratio']};{reference_optimos_hard['hyperarea_ratio']}\n"
        result += (
            f";SA;{sa_easy['hyperarea_ratio']};{sa_mid['hyperarea_ratio']};{sa_hard['hyperarea_ratio']}\n"
        )
        result += f";Tabu Search;{tabu_search_easy['hyperarea_ratio']};{tabu_search_mid['hyperarea_ratio']};{tabu_search_hard['hyperarea_ratio']}\n"
        result += (
            f";PPO;{ppo_easy['hyperarea_ratio']};{ppo_mid['hyperarea_ratio']};{ppo_hard['hyperarea_ratio']}\n"
        )
        result += f";Tabu Random;{tabu_search_random_easy['hyperarea_ratio']};{tabu_search_random_mid['hyperarea_ratio']};{tabu_search_random_hard['hyperarea_ratio']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['hyperarea_ratio']};{simulated_annealing_random_mid['hyperarea_ratio']};{simulated_annealing_random_hard['hyperarea_ratio']}\n"
        result += f";PPO Random;{ppo_random_easy['hyperarea_ratio']};{ppo_random_mid['hyperarea_ratio']};{ppo_random_hard['hyperarea_ratio']}\n\n"

        result += "Hausdorff\n"
        result += f";Reference Random;{reference_random_easy['hausdorff_distance']};{reference_random_mid['hausdorff_distance']};{reference_random_hard['hausdorff_distance']}\n"
        result += f";Reference Optimos;{reference_optimos_easy['hausdorff_distance']};{reference_optimos_mid['hausdorff_distance']};{reference_optimos_hard['hausdorff_distance']}\n"
        result += f";SA;{sa_easy['hausdorff_distance']};{sa_mid['hausdorff_distance']};{sa_hard['hausdorff_distance']}\n"
        result += f";Tabu Search;{tabu_search_easy['hausdorff_distance']};{tabu_search_mid['hausdorff_distance']};{tabu_search_hard['hausdorff_distance']}\n"
        result += f";PPO;{ppo_easy['hausdorff_distance']};{ppo_mid['hausdorff_distance']};{ppo_hard['hausdorff_distance']}\n"
        result += f";Tabu Random;{tabu_search_random_easy['hausdorff_distance']};{tabu_search_random_mid['hausdorff_distance']};{tabu_search_random_hard['hausdorff_distance']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['hausdorff_distance']};{simulated_annealing_random_mid['hausdorff_distance']};{simulated_annealing_random_hard['hausdorff_distance']}\n"
        result += f";PPO Random;{ppo_random_easy['hausdorff_distance']};{ppo_random_mid['hausdorff_distance']};{ppo_random_hard['hausdorff_distance']}\n\n"

        result += "Delta\n"
        result += f";Reference Random;{reference_random_easy['delta']};{reference_random_mid['delta']};{reference_random_hard['delta']}\n"
        result += f";Reference Optimos;{reference_optimos_easy['delta']};{reference_optimos_mid['delta']};{reference_optimos_hard['delta']}\n"
        result += f";SA;{sa_easy['delta']};{sa_mid['delta']};{sa_hard['delta']}\n"
        result += f";Tabu Search;{tabu_search_easy['delta']};{tabu_search_mid['delta']};{tabu_search_hard['delta']}\n"
        result += f";PPO;{ppo_easy['delta']};{ppo_mid['delta']};{ppo_hard['delta']}\n"
        result += f";Tabu Random;{tabu_search_random_easy['delta']};{tabu_search_random_mid['delta']};{tabu_search_random_hard['delta']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['delta']};{simulated_annealing_random_mid['delta']};{simulated_annealing_random_hard['delta']}\n"
        result += (
            f";PPO Random;{ppo_random_easy['delta']};{ppo_random_mid['delta']};{ppo_random_hard['delta']}\n\n"
        )

        result += "Purity\n"
        result += f";Reference Random;{reference_random_easy['purity']};{reference_random_mid['purity']};{reference_random_hard['purity']}\n"
        result += f";Reference Optimos;{reference_optimos_easy['purity']};{reference_optimos_mid['purity']};{reference_optimos_hard['purity']}\n"
        result += f";SA;{sa_easy['purity']};{sa_mid['purity']};{sa_hard['purity']}\n"
        result += f";Tabu Search;{tabu_search_easy['purity']};{tabu_search_mid['purity']};{tabu_search_hard['purity']}\n"
        result += f";PPO;{ppo_easy['purity']};{ppo_mid['purity']};{ppo_hard['purity']}\n"
        result += f";Tabu Random;{tabu_search_random_easy['purity']};{tabu_search_random_mid['purity']};{tabu_search_random_hard['purity']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['purity']};{simulated_annealing_random_mid['purity']};{simulated_annealing_random_hard['purity']}\n"
        result += f";PPO Random;{ppo_random_easy['purity']};{ppo_random_mid['purity']};{ppo_random_hard['purity']}\n\n"

        result += "Avg Cycle Time\n"
        result += f";Base;{reference_easy['base_cycle_time']};{reference_mid['base_cycle_time']};{reference_hard['base_cycle_time']}\n"
        result += f";Reference;{reference_easy['pareto_avg_cycle_time']};{reference_mid['pareto_avg_cycle_time']};{reference_hard['pareto_avg_cycle_time']}\n"
        result += f";Reference Random;{reference_random_easy['pareto_avg_cycle_time']};{reference_random_mid['pareto_avg_cycle_time']};{reference_random_hard['pareto_avg_cycle_time']}\n"
        result += f";Reference Optimos;{reference_optimos_easy['pareto_avg_cycle_time']};{reference_optimos_mid['pareto_avg_cycle_time']};{reference_optimos_hard['pareto_avg_cycle_time']}\n"
        result += f";SA;{sa_easy['pareto_avg_cycle_time']};{sa_mid['pareto_avg_cycle_time']};{sa_hard['pareto_avg_cycle_time']}\n"
        result += f";Tabu Search;{tabu_search_easy['pareto_avg_cycle_time']};{tabu_search_mid['pareto_avg_cycle_time']};{tabu_search_hard['pareto_avg_cycle_time']}\n"
        result += f";PPO;{ppo_easy['pareto_avg_cycle_time']};{ppo_mid['pareto_avg_cycle_time']};{ppo_hard['pareto_avg_cycle_time']}\n"
        result += f";Tabu Random;{tabu_search_random_easy['pareto_avg_cycle_time']};{tabu_search_random_mid['pareto_avg_cycle_time']};{tabu_search_random_hard['pareto_avg_cycle_time']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['pareto_avg_cycle_time']};{simulated_annealing_random_mid['pareto_avg_cycle_time']};{simulated_annealing_random_hard['pareto_avg_cycle_time']}\n"
        result += f";PPO Random;{ppo_random_easy['pareto_avg_cycle_time']};{ppo_random_mid['pareto_avg_cycle_time']};{ppo_random_hard['pareto_avg_cycle_time']}\n\n"

        result += "Best Cycle Time\n"
        result += f";Base;{reference_easy['base_cycle_time']};{reference_mid['base_cycle_time']};{reference_hard['base_cycle_time']}\n"
        result += f";Reference;{reference_easy['best_cycle_time']};{reference_mid['best_cycle_time']};{reference_hard['best_cycle_time']}\n"
        result += f";Reference Random;{reference_random_easy['best_cycle_time']};{reference_random_mid['best_cycle_time']};{reference_random_hard['best_cycle_time']}\n"
        result += f";Reference Optimos;{reference_optimos_easy['best_cycle_time']};{reference_optimos_mid['best_cycle_time']};{reference_optimos_hard['best_cycle_time']}\n"
        result += (
            f";SA;{sa_easy['best_cycle_time']};{sa_mid['best_cycle_time']};{sa_hard['best_cycle_time']}\n"
        )
        result += f";Tabu Search;{tabu_search_easy['best_cycle_time']};{tabu_search_mid['best_cycle_time']};{tabu_search_hard['best_cycle_time']}\n"
        result += (
            f";PPO;{ppo_easy['best_cycle_time']};{ppo_mid['best_cycle_time']};{ppo_hard['best_cycle_time']}\n"
        )
        result += f";Tabu Random;{tabu_search_random_easy['best_cycle_time']};{tabu_search_random_mid['best_cycle_time']};{tabu_search_random_hard['best_cycle_time']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['best_cycle_time']};{simulated_annealing_random_mid['best_cycle_time']};{simulated_annealing_random_hard['best_cycle_time']}\n"
        result += f";PPO Random;{ppo_random_easy['best_cycle_time']};{ppo_random_mid['best_cycle_time']};{ppo_random_hard['best_cycle_time']}\n\n"

        result += f"Best Avg Cycle Time\n"
        result += f";Base;{reference_easy['base_avg_cycle_time']};{reference_mid['base_avg_cycle_time']};{reference_hard['base_avg_cycle_time']}\n"
        result += f";Reference;{reference_easy['best_avg_cycle_time']};{reference_mid['best_avg_cycle_time']};{reference_hard['best_avg_cycle_time']}\n"
        result += f";Reference Random;{reference_random_easy['best_avg_cycle_time']};{reference_random_mid['best_avg_cycle_time']};{reference_random_hard['best_avg_cycle_time']}\n"
        result += f";Reference Optimos;{reference_optimos_easy['best_avg_cycle_time']};{reference_optimos_mid['best_avg_cycle_time']};{reference_optimos_hard['best_avg_cycle_time']}\n"
        result += f";SA;{sa_easy['best_avg_cycle_time']};{sa_mid['best_avg_cycle_time']};{sa_hard['best_avg_cycle_time']}\n"
        result += f";Tabu Search;{tabu_search_easy['best_avg_cycle_time']};{tabu_search_mid['best_avg_cycle_time']};{tabu_search_hard['best_avg_cycle_time']}\n"
        result += f";PPO;{ppo_easy['best_avg_cycle_time']};{ppo_mid['best_avg_cycle_time']};{ppo_hard['best_avg_cycle_time']}\n"
        result += f";Tabu Random;{tabu_search_random_easy['best_avg_cycle_time']};{tabu_search_random_mid['best_avg_cycle_time']};{tabu_search_random_hard['best_avg_cycle_time']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['best_avg_cycle_time']};{simulated_annealing_random_mid['best_avg_cycle_time']};{simulated_annealing_random_hard['best_avg_cycle_time']}\n"
        result += f";PPO Random;{ppo_random_easy['best_avg_cycle_time']};{ppo_random_mid['best_avg_cycle_time']};{ppo_random_hard['best_avg_cycle_time']}\n\n"

        result += f"Best {Settings.get_pareto_x_label()}\n"
        result += f";Base;{reference_easy['base_x']};{reference_mid['base_x']};{reference_hard['base_x']}\n"
        result += (
            f";Reference;{reference_easy['best_x']};{reference_mid['best_x']};{reference_hard['best_x']}\n"
        )
        result += f";Reference Random;{reference_random_easy['best_x']};{reference_random_mid['best_x']};{reference_random_hard['best_x']}\n"
        result += f";Reference Optimos;{reference_optimos_easy['best_x']};{reference_optimos_mid['best_x']};{reference_optimos_hard['best_x']}\n"
        result += f";SA;{sa_easy['best_x']};{sa_mid['best_x']};{sa_hard['best_x']}\n"
        result += f";Tabu Search;{tabu_search_easy['best_x']};{tabu_search_mid['best_x']};{tabu_search_hard['best_x']}\n"
        result += f";PPO;{ppo_easy['best_x']};{ppo_mid['best_x']};{ppo_hard['best_x']}\n"
        result += f";Tabu Random;{tabu_search_random_easy['best_x']};{tabu_search_random_mid['best_x']};{tabu_search_random_hard['best_x']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['best_x']};{simulated_annealing_random_mid['best_x']};{simulated_annealing_random_hard['best_x']}\n"
        result += f";PPO Random;{ppo_random_easy['best_x']};{ppo_random_mid['best_x']};{ppo_random_hard['best_x']}\n\n"

        result += f"Best {Settings.get_pareto_y_label()}\n"
        result += f";Base;{reference_easy['base_y']};{reference_mid['base_y']};{reference_hard['base_y']}\n"
        result += (
            f";Reference;{reference_easy['best_y']};{reference_mid['best_y']};{reference_hard['best_y']}\n"
        )
        result += f";Reference Random;{reference_random_easy['best_y']};{reference_random_mid['best_y']};{reference_random_hard['best_y']}\n"
        result += f";Reference Optimos;{reference_optimos_easy['best_y']};{reference_optimos_mid['best_y']};{reference_optimos_hard['best_y']}\n"
        result += f";SA;{sa_easy['best_y']};{sa_mid['best_y']};{sa_hard['best_y']}\n"
        result += f";Tabu Search;{tabu_search_easy['best_y']};{tabu_search_mid['best_y']};{tabu_search_hard['best_y']}\n"
        result += f";PPO;{ppo_easy['best_y']};{ppo_mid['best_y']};{ppo_hard['best_y']}\n"
        result += f";Tabu Random;{tabu_search_random_easy['best_y']};{tabu_search_random_mid['best_y']};{tabu_search_random_hard['best_y']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['best_y']};{simulated_annealing_random_mid['best_y']};{simulated_annealing_random_hard['best_y']}\n"
        result += f";PPO Random;{ppo_random_easy['best_y']};{ppo_random_mid['best_y']};{ppo_random_hard['best_y']}\n\n"

        result += f"Avg {Settings.get_pareto_x_label()}\n"
        result += f";Base;{reference_easy['base_x']};{reference_mid['base_x']};{reference_hard['base_x']}\n"
        result += f";Reference;{reference_easy['avg_x']};{reference_mid['avg_x']};{reference_hard['avg_x']}\n"
        result += f";Reference Random;{reference_random_easy['avg_x']};{reference_random_mid['avg_x']};{reference_random_hard['avg_x']}\n"
        result += f";Reference Optimos;{reference_optimos_easy['avg_x']};{reference_optimos_mid['avg_x']};{reference_optimos_hard['avg_x']}\n"
        result += f";SA;{sa_easy['avg_x']};{sa_mid['avg_x']};{sa_hard['avg_x']}\n"
        result += f";Tabu Search;{tabu_search_easy['avg_x']};{tabu_search_mid['avg_x']};{tabu_search_hard['avg_x']}\n"
        result += f";PPO;{ppo_easy['avg_x']};{ppo_mid['avg_x']};{ppo_hard['avg_x']}\n"
        result += f";Tabu Random;{tabu_search_random_easy['avg_x']};{tabu_search_random_mid['avg_x']};{tabu_search_random_hard['avg_x']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['avg_x']};{simulated_annealing_random_mid['avg_x']};{simulated_annealing_random_hard['avg_x']}\n"
        result += (
            f";PPO Random;{ppo_random_easy['avg_x']};{ppo_random_mid['avg_x']};{ppo_random_hard['avg_x']}\n\n"
        )

        result += f"Avg {Settings.get_pareto_y_label()}\n"
        result += f";Base;{reference_easy['base_y']};{reference_mid['base_y']};{reference_hard['base_y']}\n"
        result += f";Reference;{reference_easy['avg_y']};{reference_mid['avg_y']};{reference_hard['avg_y']}\n"
        result += f";Reference Random;{reference_random_easy['avg_y']};{reference_random_mid['avg_y']};{reference_random_hard['avg_y']}\n"
        result += f";Reference Optimos;{reference_optimos_easy['avg_y']};{reference_optimos_mid['avg_y']};{reference_optimos_hard['avg_y']}\n"
        result += f";SA;{sa_easy['avg_y']};{sa_mid['avg_y']};{sa_hard['avg_y']}\n"
        result += f";Tabu Search;{tabu_search_easy['avg_y']};{tabu_search_mid['avg_y']};{tabu_search_hard['avg_y']}\n"
        result += f";PPO;{ppo_easy['avg_y']};{ppo_mid['avg_y']};{ppo_hard['avg_y']}\n"
        result += f";Tabu Random;{tabu_search_random_easy['avg_y']};{tabu_search_random_mid['avg_y']};{tabu_search_random_hard['avg_y']}\n"
        result += f";SA Random;{simulated_annealing_random_easy['avg_y']};{simulated_annealing_random_mid['avg_y']};{simulated_annealing_random_hard['avg_y']}\n"
        result += (
            f";PPO Random;{ppo_random_easy['avg_y']};{ppo_random_mid['avg_y']};{ppo_random_hard['avg_y']}\n\n"
        )

    final_result_str = result.replace(".", ",")
    print(final_result_str)
    with open("o2_evaluation/markdown_creator/analyzer_report.ssv", "w") as f:
        f.write(final_result_str)


if __name__ == "__main__":
    Settings.LOG_LEVEL = "IO"
    Settings.LOG_FILE = "logs/data_analyzer.log"
    Settings.COST_TYPE = CostType.AVG_WT_AND_PT_PER_TASK_INSTANCE
    Settings.ARCHIVE_SOLUTIONS = True
    Settings.DELETE_LOADED_SOLUTION_ARCHIVES = False
    Settings.OVERWRITE_EXISTING_SOLUTION_ARCHIVES = False
    Settings.CHECK_FOR_TIMETABLE_EQUALITY = True
    setup_logging()

    SolutionDumper(global_mode=True)

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
        mode = get_mode_from_scenario(scenario)
        scenario_without_mode = get_scenario_without_mode(scenario)

        # if not ("gov" in scenario.lower() or "2019" in scenario.lower() or "sepsis" in scenario.lower()):
        #     continue

        if not "2019" in scenario.lower():
            continue

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
