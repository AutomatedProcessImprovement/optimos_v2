import gc
import glob
import pickle
from collections import defaultdict

from o2.models.settings import CostType, Settings
from o2.models.solution import Solution
from o2.store import Store
from o2.util.logger import info, setup_logging, warn
from o2_evaluation.data_collector import calculate_metrics


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
        raise ValueError(f"Invalid filename: {filename}")
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

    for scenario in scenarios:
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
        calculate_metrics(stores, solutions)
        info(f"Finished processing scenario: {scenario}; Collecting garbage...")
