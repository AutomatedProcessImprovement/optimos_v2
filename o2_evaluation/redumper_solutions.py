import gc
import glob
import os
import pickle

from o2.models.settings import CostType, Settings
from o2.store import Store
from o2.util.logger import info, setup_logging
from o2.util.solution_dumper import SolutionDumper

SKIP = []

if __name__ == "__main__":
    Settings.LOG_LEVEL = "DEBUG"
    Settings.LOG_FILE = "logs/redumper.log"
    Settings.COST_TYPE = CostType.WAITING_TIME_AND_PROCESSING_TIME
    Settings.ARCHIVE_SOLUTIONS = True
    Settings.CHECK_FOR_TIMETABLE_EQUALITY = True
    Settings.DELETE_LOADED_SOLUTION_ARCHIVES = True
    Settings.OVERWRITE_EXISTING_SOLUTION_ARCHIVES = False
    setup_logging()

    SolutionDumper(analysis_mode=True)

    # gc.disable()
    # Get all subfiles in the analyze_stores directory
    analyze_stores_dir = "o2_evaluation/redumped_stores"
    analyze_stores_file_list = glob.glob(f"{analyze_stores_dir}/**store_*.pkl")
    dump_dir = "o2_evaluation/redumped_stores"
    for file in analyze_stores_file_list:
        if any(skip in file for skip in SKIP):
            info(f"Skipping file: {file}")
            continue

        info(f"Loading file: {file}...")

        with open(file, "rb") as f:
            store: Store = pickle.load(f)
        info(f"Updating store name to: {store.name}...")
        SolutionDumper.instance.update_store_name(store.name)

        solutions = store.solution_tree.solution_lookup.values()
        info(f"Archiving {len(solutions)} solutions...")
        i = 0
        for solution in solutions:
            i += 1
            if solution is None:
                continue
            if solution in store.current_pareto_front.solutions:
                continue
            # Force the evaluation of hash
            hash(solution)
            # Force evaluation of point
            solution.point  # noqa: B018
            solution.pareto_x  # noqa: B018
            solution.pareto_y  # noqa: B018

            solution.archive()
            if i % 1000 == 0:
                info(f"Archived {i} solutions...")
        info(f"Dumping store...")
        SolutionDumper.instance.dump_store(store)
        info(f"Done processing file: {file}")
