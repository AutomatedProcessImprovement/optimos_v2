import gc
import glob
import pickle

from o2.models.solution import Solution
from o2.store import Store
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
    gc.disable()
    # Get all subfiles in the analyze_stores directory
    analyze_stores_dir = "o2_evaluation/analyze_stores"
    analyze_stores_files = glob.glob(f"{analyze_stores_dir}/**store_*.pkl")
    solution_files = glob.glob(f"{analyze_stores_dir}/**solutions_*.pkl")
    # Scenario, Model, Store
    stores: list[tuple[str, str, Store]] = []
    solutions: list[tuple[str, str, Solution]] = []
    scenarios: set[str] = set()
    for file in analyze_stores_files:
        print(
            f"Loading store from {file}... ({get_scenario_from_filename(file)}, {get_model_from_filename(file)})"
        )
        with open(file, "rb") as f:
            try:
                store = pickle.load(f)
                stores.append(
                    (
                        get_scenario_from_filename(file),
                        get_model_from_filename(file),
                        store,
                    )
                )
                scenarios.add(get_scenario_from_filename(file))
                print(f"Loaded store '{store.name}' from {file}")
            except Exception as e:
                print(f"Error loading store from {file}: {e}")

    for file in solution_files:
        with open(file, "rb") as f:
            print(f"Loading solutions from {file}...")
            while True:
                try:
                    solution = pickle.load(f)
                    solutions.append(
                        (
                            get_scenario_from_filename(file),
                            get_model_from_filename(file),
                            solution,
                        )
                    )
                except EOFError:
                    break
                except Exception as e:
                    print(f"Error loading (more) solutions from {file}: {e}")
                    break
            print("Done!")

    print(f"Loaded {len(stores)} stores and {len(solutions)} solutions")

    # Calculate the metrics for the given stores
    for scenario in scenarios:
        stores_of_scenario = [
            (model, store) for (s, model, store) in stores if s == scenario
        ]
        solutions_of_scenario = [
            solution for (s, _, solution) in solutions if s == scenario
        ]
        calculate_metrics(stores_of_scenario, solutions_of_scenario)
