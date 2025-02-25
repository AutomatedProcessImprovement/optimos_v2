import gc
import glob
import pickle
from collections import defaultdict

from o2.models.settings import CostType, Settings
from o2.models.solution import Solution
from o2.store import Store
from o2.util.logger import info, setup_logging, warn
from o2_evaluation.data_collector import Metrics, calculate_metrics


def get_model_from_filename(path: str) -> str:
    filename = path.split("/")[-1]
    if not filename.startswith("store_") and not filename.startswith("solutions_"):
        raise ValueError(f"Invalid filename: {filename}")
    if "tabu_search" in filename:
        return "Tabu Search"
    elif "simulated_annealing" in filename:
        return "Simulated Annealing"
    elif "proximal_policy_optimization" in filename:
        return "Proximal Policy Optimization"
    else:
        raise ValueError(f"Invalid filename: {filename}")


def get_scenario_from_filename(path: str) -> str:
    # o2_evaluation/analyze_stores/store_simulated_annealing_bpi_challenge_2012_hard.pkl
    filename = path.split("/")[-1]
    if not filename.startswith("store_") and not filename.startswith("solutions_"):
        raise ValueError(f"Invalid filename: {path}")
    return (
        filename.replace("store_", "")
        .replace("solutions_", "")
        .replace(".pkl", "")
        .replace("tabu_search_", "")
        .replace("simulated_annealing_", "")
        .replace("proximal_policy_optimization_", "")
        .replace("_", " ")
        .title()
    )


def get_scenario_without_mode(scenario: str) -> str:
    return (
        scenario.lower().replace("_easy", "").replace("_mid", "").replace("_hard", "")
    )


def print_metrics_in_google_sheet_format(metrics: list[Metrics]) -> None:
    # Print the metrics in google sheet format
    # For Reference:

    # Group solutions, that have the same scenario (but different _easy, _mid, _hard)
    grouped_metrics = defaultdict(list)
    for metric in metrics:
        grouped_metrics[get_scenario_without_mode(metric["store_name"])].append(metric)

    result = "Pareto Metrics\tEasy\tMid\tHard"
    for scenario, metrics in grouped_metrics.items():
        print(f"Sheet: {scenario}")
        assert len(metrics) == 4
        reference = next(m for m in metrics if "Reference" in m["store_name"])
        hard = next(m for m in metrics if "hard" in m["store_name"])
        mid = next(m for m in metrics if "mid" in m["store_name"])
        easy = next(m for m in metrics if "easy" in m["store_name"])

        result += f"\n{scenario}\t{len(easy)}\t{len(mid)}\t{len(hard)}\n\n"
        result += "Pareto Size\n"
        result += f"\tReference\t{reference['patreto_size']}\t{mid['patreto_size']}\t{hard['patreto_size']}\n"
        result += f"\tSA\t{easy['patreto_size']}\t{mid['patreto_size']}\t{hard['patreto_size']}\n"
        result += f"\tTabu Search\t{easy['patreto_size']}\t{mid['patreto_size']}\t{hard['patreto_size']}\n"
        result += f"\tPPO\t{easy['patreto_size']}\t{mid['patreto_size']}\t{hard['patreto_size']}\n\n"
        result += "Hyperarea\n"
        result += f"\tReference\t{reference['hyperarea']}\t{mid['hyperarea']}\t{hard['hyperarea']}\n"
        result += (
            f"\tSA\t{easy['hyperarea']}\t{mid['hyperarea']}\t{hard['hyperarea']}\n"
        )
        result += f"\tTabu Search\t{easy['hyperarea']}\t{mid['hyperarea']}\t{hard['hyperarea']}\n"
        result += (
            f"\tPPO\t{easy['hyperarea']}\t{mid['hyperarea']}\t{hard['hyperarea']}\n\n"
        )
        result += "Hausdorff\n"
        result += f"\tReference\t{reference['hausdorff_distance']}\t{mid['hausdorff_distance']}\t{hard['hausdorff_distance']}\n"
        result += f"\tSA\t{easy['hausdorff_distance']}\t{mid['hausdorff_distance']}\t{hard['hausdorff_distance']}\n"
        result += f"\tTabu Search\t{easy['hausdorff_distance']}\t{mid['hausdorff_distance']}\t{hard['hausdorff_distance']}\n"
        result += f"\tPPO\t{easy['hausdorff_distance']}\t{mid['hausdorff_distance']}\t{hard['hausdorff_distance']}\n\n"
        result += "Delta\n"
        result += (
            f"\tReference\t{reference['delta']}\t{mid['delta']}\t{hard['delta']}\n"
        )
        result += f"\tSA\t{easy['delta']}\t{mid['delta']}\t{hard['delta']}\n"
        result += f"\tTabu Search\t{easy['delta']}\t{mid['delta']}\t{hard['delta']}\n"
        result += f"\tPPO\t{easy['delta']}\t{mid['delta']}\t{hard['delta']}\n\n"
        result += "Purity\n"
        result += (
            f"\tReference\t{reference['purity']}\t{mid['purity']}\t{hard['purity']}\n"
        )
        result += f"\tSA\t{easy['purity']}\t{mid['purity']}\t{hard['purity']}\n"
        result += (
            f"\tTabu Search\t{easy['purity']}\t{mid['purity']}\t{hard['purity']}\n"
        )
        result += f"\tPPO\t{easy['purity']}\t{mid['purity']}\t{hard['purity']}\n\n"
    print(result)


if __name__ == "__main__":
    Settings.LOG_LEVEL = "DEBUG"
    Settings.LOG_FILE = "logs/data_analyzer.log"
    Settings.COST_TYPE = CostType.WAITING_TIME_AND_PROCESSING_TIME
    setup_logging()

    gc.disable()
    # Get all subfiles in the analyze_stores directory
    analyze_stores_dir = "o2_evaluation/analyze_stores"
    analyze_stores_file_list = glob.glob(f"{analyze_stores_dir}/**store_*.pkl")
    solution_files_list = glob.glob(f"{analyze_stores_dir}/**solutions_*.pkl")
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
        # Skip callcentre scenarios for now
        if "callcentre" in scenario.lower():
            continue
        info(f"Processing scenario: {scenario}")
        stores: list[tuple[str, Store]] = []
        solutions: list[Solution] = []
        for file in stores_files[scenario]:
            info(
                f"Loading store from {file}... ({get_scenario_from_filename(file)}, {get_model_from_filename(file)})"
            )
            with open(file, "rb") as f:
                try:
                    store = pickle.load(f)
                    stores.append(
                        (
                            get_model_from_filename(file),
                            store,
                        )
                    )
                    info(f"Loaded store '{store.name}' from {file}")
                except Exception as e:
                    warn(f"Error loading store from {file}: {e}")

        for file in solutions_files[scenario]:
            with open(file, "rb") as f:
                info(f"Loading solutions from {file}...")
                while True:
                    try:
                        solution = pickle.load(f)
                        solutions.append(solution)
                    except EOFError:
                        break
                    except Exception as e:
                        warn(f"Error loading (more) solutions from {file}: {e}")
                        break
                info("Done!")

        info(f"Loaded {len(stores)} stores and {len(solutions)} solutions")

        # Calculate the metrics for the given stores
        metrics = calculate_metrics(stores, solutions)
        all_metrics.extend(metrics)

    pickle.dump(all_metrics, open("all_metrics.pkl", "wb"))
    # Print the metrics in google sheet format
    print_metrics_in_google_sheet_format(all_metrics)
