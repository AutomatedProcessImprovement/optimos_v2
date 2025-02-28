"""The script will redump the solutions from the analyze_stores directory.

It will also archive the solutions to the archive directory.
"""

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
    Settings.DELETE_LOADED_SOLUTION_ARCHIVES = False
    Settings.OVERWRITE_EXISTING_SOLUTION_ARCHIVES = False
    setup_logging()

    SolutionDumper(analysis_mode=True)

    # gc.disable()
    # Get all subfiles in the analyze_stores directory
    analyze_stores_dir = "o2_evaluation/analyze_stores"
    analyze_stores_file_list = glob.glob(f"{analyze_stores_dir}/**solutions_*.pkl")
    dump_dir = "o2_evaluation/redumped_stores"
    for file in analyze_stores_file_list:
        file_name = file.split("/")[-1]
        if any(skip in file for skip in SKIP):
            info(f"Skipping file: {file}")
            continue

        output_file = os.path.join(dump_dir, file_name)
        if os.path.exists(output_file):
            info(f"File already exists: {output_file}")
            continue

        info(f"Loading file: {file}...")

        with open(file, "rb") as f:
            solutions = []
            while True:
                try:
                    solution = pickle.load(f)
                    solutions.append(solution)
                except EOFError:
                    break

        info(f"Archiving {len(solutions)} solutions...")
        i = 0
        for solution in solutions:
            i += 1
            if solution is None:
                continue
            # Force the evaluation of hash
            hash(solution)
            # Force evaluation of pareto_x and pareto_y
            solution.pareto_x  # noqa: B018
            solution.pareto_y  # noqa: B018
            # Force evaluation of point
            solution.point  # noqa: B018
            if i % 100 == 0:
                info(f"Processed {i} solutions...")

        print("start writing solutions file")

        i = 0
        with open(output_file, "wb") as f:
            for solution in solutions:
                pickle.dump(solution, f)
                i += 1
                if i % 100 == 0:
                    info(f"Wrote {i} solutions...")

        info(f"Done processing file: {file}")
