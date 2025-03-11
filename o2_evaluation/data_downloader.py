import gc
import glob
import os
import pickle
import subprocess
import sys
import tempfile
from collections import defaultdict

from o2.models.settings import CostType, Settings
from o2.models.solution import Solution
from o2.store import Store
from o2.util.logger import debug, info, setup_logging, warn
from o2.util.solution_dumper import SolutionDumper
from o2_evaluation.data_analyzer import (
    get_agent_from_filename,
    get_scenario_from_filename,
)

# Config
REMOTE_HOST = "rocket.hpc.ut.ee"
REMOTE_USER = "jannis"
REMOTE_PATH = "~/optimos_v2"
SSH_KEY = "~/.ssh/id_rocket"
REMOTE_LIST_FILE = "remote_file_list.txt"
LOCAL_LIST_FILE = "local_file_list.txt"
LOCAL_OUTPUT_DIR = "evaluations"


def get_stores_and_solutions():
    """Get the stores and solutions from the local directory."""
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

    for scenario in scenarios:
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
        yield stores, solutions


def find_required_files() -> list[str]:
    """Find the required files for the given stores and solutions."""
    # Create a temporary directory
    required_files: list[str] = []

    for stores, extra_solutions in get_stores_and_solutions():
        all_solutions: set[Solution] = set()

        for _, store in stores:
            store_solutions = [
                *store.solution_tree.solution_lookup.values(),
                *[s for pareto in store.pareto_fronts for s in pareto.solutions],
            ]
            for solution in store_solutions:
                if solution is not None and solution.is_valid:
                    # Add store name so we can load the evaluation and state later
                    solution.__dict__["_store_name"] = store.name
                    all_solutions.add(solution)

        all_solutions.update(
            [extra_solution for extra_solution in extra_solutions if extra_solution.is_valid]
        )

        # Find the Pareto front (non-dominated solutions)
        all_solutions_front = [
            solution
            for solution in all_solutions
            if not any(
                solution.is_dominated_by(other)
                for other in all_solutions
                if (Settings.EQUAL_DOMINATION_ALLOWED or other.point != solution.point)
            )
        ]

        required_solutions = (
            # Add every non-dominated solution from the reference front
            all_solutions_front
            # Add every solution of the current Pareto front from each store
            + [solution for _, store in stores for solution in store.current_pareto_front.solutions]
            # Add base solution from each store
            + [store.base_solution for _, store in stores if store.base_solution is not None]
        )

        # List of paths to the required files
        required_files.extend(
            set(
                [
                    f"evaluation_{solution.__dict__['_store_name'].replace(' ', '_').lower()}_{solution.id}.pkl"
                    for solution in required_solutions
                ]
            )
        )

    return required_files


def run_command(cmd: str) -> None:
    """Run a command and print the output."""
    print(f"Running: {cmd}")

    process = subprocess.Popen(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)
    process.wait()  # Wait for the process to finish

    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, cmd)


def copy_file_to_remote(file_path: str) -> None:
    """Copy a file to the remote host."""
    cmd = f"scp -i {SSH_KEY} {file_path} {REMOTE_USER}@{REMOTE_HOST}:{REMOTE_LIST_FILE}"
    run_command(cmd)


def find_files_on_remote() -> None:
    """Find the files on the remote host."""
    find_command = (
        f"ssh -i {SSH_KEY} {REMOTE_USER}@{REMOTE_HOST} "
        f'"find ~/optimos_v2/stores/*/evaluations/ -type f | grep -F -f {REMOTE_LIST_FILE} > ~/full_paths.txt"'
    )
    run_command(find_command)


def copy_file_back_to_local() -> None:
    """Copy a file back to the local host."""
    cmd = f"scp -i {SSH_KEY} {REMOTE_USER}@{REMOTE_HOST}:~/full_paths.txt {LOCAL_LIST_FILE}"
    run_command(cmd)


def run_rsync() -> None:
    """Run rsync to copy files flat into "evaluations/"."""
    cmd = (
        f'rsync -e "ssh -i {SSH_KEY}" -avhz --progress '
        f"--files-from={LOCAL_LIST_FILE} --no-relative {REMOTE_USER}@{REMOTE_HOST}:/ {LOCAL_OUTPUT_DIR}/"
    )
    run_command(cmd)


def main() -> None:
    """Execute main logic."""
    Settings.LOG_LEVEL = "IO"
    Settings.LOG_FILE = "logs/data_downloader.log"
    Settings.COST_TYPE = CostType.AVG_WT_AND_PT_PER_TASK_INSTANCE
    Settings.ARCHIVE_SOLUTIONS = True
    Settings.DELETE_LOADED_SOLUTION_ARCHIVES = False
    Settings.OVERWRITE_EXISTING_SOLUTION_ARCHIVES = False
    Settings.CHECK_FOR_TIMETABLE_EQUALITY = True
    setup_logging()

    SolutionDumper(global_mode=True)

    gc.disable()

    os.makedirs(LOCAL_OUTPUT_DIR, exist_ok=True)

    required_files = find_required_files()
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write("\n".join(required_files).encode("utf-8"))

    print(f"Temporary file: {f.name}")

    # 1. Copy file with list of filenames to remote
    copy_file_to_remote(f.name)

    # 2. Run find command on remote to get full paths
    find_files_on_remote()

    # 3. Copy full paths file back to local
    copy_file_back_to_local()

    # 4. Run rsync to copy files flat into "evaluations/"
    run_rsync()


if __name__ == "__main__":
    main()
