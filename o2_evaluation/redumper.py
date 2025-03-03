import gc
import glob
import os
import pickle
import traceback

from o2.models.settings import CostType, Settings
from o2.store import Store
from o2.util.logger import error, info, setup_logging
from o2.util.solution_dumper import SolutionDumper

SKIP = []

if __name__ == "__main__":
    Settings.LOG_LEVEL = "DEBUG"
    Settings.LOG_FILE = "logs/redumper.log"
    Settings.COST_TYPE = CostType.AVG_WT_AND_PT_PER_TASK_INSTANCE
    Settings.ARCHIVE_SOLUTIONS = True
    Settings.DELETE_LOADED_SOLUTION_ARCHIVES = False
    Settings.OVERWRITE_EXISTING_SOLUTION_ARCHIVES = False  # TDOO
    Settings.CHECK_FOR_TIMETABLE_EQUALITY = True
    setup_logging()

    SolutionDumper(analysis_mode=True)

    # gc.disable()
    # Get all subfiles in the analyze_stores directory
    analyze_stores_dir = "o2_evaluation/analyze_stores"
    analyze_stores_file_list = glob.glob(f"{analyze_stores_dir}/**store_*.pkl")
    dump_dir = "o2_evaluation/redumped_stores"
    for file in analyze_stores_file_list:
        try:
            if any(skip in file for skip in SKIP):
                info(f"Skipping file: {file}")
                continue

            file_name = file.split("/")[-1]
            if os.path.exists(os.path.join(dump_dir, file_name)):
                info(f"File already exists: {file_name}")
                continue

            info(f"Loading file: {file}...")
            with open(file, "rb") as f:
                store: Store = pickle.load(f)
            info(f"Updating store name to: {store.name}...")
            SolutionDumper.instance.update_store_name(store.name)
            pareto_front = store.current_pareto_front
            solutions = store.solution_tree.solution_lookup.values()
            info(f"Archiving {len(solutions)} solutions...")
            i = 0
            for solution in solutions:
                if solution is None:
                    continue
                if solution in pareto_front.solutions:
                    continue
                # Force the evaluation of hash
                hash(solution)
                # Force evaluation of pareto_x and pareto_y
                solution.pareto_x  # noqa: B018
                solution.pareto_y  # noqa: B018
                # Force evaluation of point
                solution.point  # noqa: B018
                solution.archive()
                i += 1
                if i % 1000 == 0:
                    info(f"Archived {i} solutions...")
            info(f"Dumping store...")
            SolutionDumper.instance.dump_store(store)
            info(f"Done processing file: {file}")
        except Exception as e:
            error(f"Error processing file: {file}")
            error(f"Error: {e}")
            error(traceback.format_exc())
