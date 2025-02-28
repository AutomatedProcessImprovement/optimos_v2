import glob
import os
import pickle
from datetime import datetime
from io import BufferedWriter, TextIOWrapper
from typing import TYPE_CHECKING, Optional

from o2.models.evaluation import Evaluation
from o2.models.settings import Settings
from o2.models.state import State

if TYPE_CHECKING:
    from o2.models.solution import Solution
    from o2.store import Store


class SolutionDumper:
    """Helper class to dump solutions and store state to disk for backup purposes."""

    instance: "SolutionDumper"

    def __init__(self, analysis_mode: bool = False) -> None:
        """Initialize the solution dumper.

        Creates a folder with the current date and time, and initializes file handles.
        Also sets the singleton instance.
        """
        self.analysis_mode = analysis_mode
        if self.analysis_mode:
            self.evaluation_paths = glob.glob(
                "evaluation_*.pkl", root_dir="./evaluations"
            )
            self.state_paths = glob.glob("state_*.pkl", root_dir="./states")
            print(f"Found {len(self.evaluation_paths)} evaluation paths.")
            print(f"Found {len(self.state_paths)} state paths.")
            self.folder = os.path.join("o2_evaluation", "redumped_stores")

        else:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            self.folder = os.path.join("stores", f"run_{timestamp}")
        self.evaluation_folder = "evaluations/"
        self.state_folder = "states/"
        os.makedirs(self.folder, exist_ok=True)
        os.makedirs(self.evaluation_folder, exist_ok=True)
        os.makedirs(self.state_folder, exist_ok=True)

        # Filenames and file handles (initialized later)
        self.current_store_name: Optional[str] = None
        self.sanitized_current_store_name: str = ""
        self.store_filename: str = ""
        self.store_stats_filename: str = ""
        self.solutions_filename: str = ""
        self.store_file: Optional[BufferedWriter] = None
        self.store_stats_file: Optional[TextIOWrapper] = None
        self.solutions_file: Optional[BufferedWriter] = None

        # Set singleton instance
        SolutionDumper.instance = self

    def dump_solution(self, solution: "Solution") -> None:
        """Dump a solution to the solutions file."""
        assert self.solutions_file is not None

        # Make sure, that the solution is archived.
        solution.archive()

        pickle.dump(solution, self.solutions_file)
        self.solutions_file.flush()

    def update_store_name(self, store_name: str) -> None:
        """Update the store name."""
        self._reset_files(store_name)

    def _open_files(self, store_name: str) -> None:
        # Open new files.
        self.store_file = open(self.store_filename, "wb")  # noqa: SIM115
        if not self.analysis_mode:
            self.store_stats_file = open(self.store_stats_filename, "w")  # noqa: SIM115
            self.solutions_file = open(self.solutions_filename, "ab")  # noqa: SIM115

    def _reset_files(self, store_name: str) -> None:
        """Close existing files and open new ones based on the new store name."""
        # Close existing files if open.
        self.close()

        # Sanitize the store name for filenames.
        sanitized_name = store_name.replace(" ", "_").lower()
        self.store_filename = os.path.join(self.folder, f"store_{sanitized_name}.pkl")
        self.store_stats_filename = os.path.join(
            self.folder, f"store_{sanitized_name}_stats.txt"
        )
        self.solutions_filename = os.path.join(
            self.folder, f"solutions_{sanitized_name}.pkl"
        )

        if not self.analysis_mode:
            self._open_files(store_name)

        self.current_store_name = store_name
        self.sanitized_current_store_name = sanitized_name

    def dump_store(self, store: "Store") -> None:
        """Dump the current store state to disk."""
        # Reset file handles if the store name has changed.
        if store.name != self.current_store_name:
            self._reset_files(store.name)

        # Ensure file handles are available.
        if (
            self.store_file is None
            or self.store_stats_file is None
            or self.solutions_file is None
        ):
            if self.analysis_mode:
                self._open_files(store.name)
                assert self.store_file is not None
            else:
                raise RuntimeError("File handles are not properly initialized.")

        # Dump the store object.
        self.store_file.seek(0)
        pickle.dump(store, self.store_file)
        self.store_file.flush()

        # Prepare store statistics.
        batching_rules = store.current_timetable.batching_rules_debug_str()
        actions = "\n".join(
            f"{i}:\t{repr(action)}"
            for i, action in enumerate(reversed(store.solution.actions))
        )
        timetable_json = store.current_timetable.to_json()

        stats = (
            "Current Batching Rules:\n"
            f"{batching_rules}\n\n"
            "All Actions:\n"
            f"{actions}\n\n"
            "Current Timetable:\n"
            f"{timetable_json}"
        )

        if not self.analysis_mode:
            assert self.store_stats_file is not None
            # Write the store statistics.
            self.store_stats_file.seek(0)
            self.store_stats_file.write(stats)
            self.store_stats_file.flush()

        if self.analysis_mode:
            self.close()

    def close(self) -> None:
        """Close any open file handles."""
        if self.store_file is not None:
            self.store_file.close()
            self.store_file = None
        if self.store_stats_file is not None:
            self.store_stats_file.close()
            self.store_stats_file = None
        if self.solutions_file is not None:
            self.solutions_file.close()
            self.solutions_file = None

    def load_store(self) -> "Store":
        """Load the store from the store file."""
        with open(self.store_filename, "rb") as f:
            return pickle.load(f)

    def load_solutions(self) -> list["Solution"]:
        """Load all solutions from the solutions file."""
        solutions = []
        with open(self.solutions_filename, "rb") as f:
            while True:
                try:
                    solution = pickle.load(f)
                    solutions.append(solution)
                except EOFError:
                    break
        return solutions

    def dump_evaluation(self, solution_id: int, evaluation: Evaluation) -> None:
        """Dump an evaluation to the evaluation file."""
        filename = os.path.join(
            self.evaluation_folder,
            f"evaluation_{self.sanitized_current_store_name}_{solution_id}.pkl",
        )
        # As we identify the solution by its id, we don't need to dump the
        # evaluation if it already exists.
        if (
            os.path.exists(filename)
            and not Settings.OVERWRITE_EXISTING_SOLUTION_ARCHIVES
        ):
            return
        with open(filename, "wb") as f:
            pickle.dump(evaluation, f)

    def _find_evaluation_filename(self, solution_id: int) -> str:
        """Find the filename of the evaluation for a given solution id."""
        best_guess_name = (
            f"evaluation_{self.sanitized_current_store_name}_{solution_id}.pkl"
        )

        if os.path.exists(os.path.join(self.evaluation_folder, best_guess_name)):
            return os.path.join(self.evaluation_folder, best_guess_name)

        path = next(
            (p for p in self.evaluation_paths if p.endswith(f"{solution_id}.pkl")),
            None,
        )
        if path is None:
            raise FileNotFoundError(f"Evaluation for solution {solution_id} not found.")
        return os.path.join(self.evaluation_folder, path)

    def _find_state_filename(self, solution_id: int) -> str:
        """Find the filename of the state for a given solution id."""
        best_guess_name = f"state_{self.sanitized_current_store_name}_{solution_id}.pkl"
        if os.path.exists(os.path.join(self.state_folder, best_guess_name)):
            return os.path.join(self.state_folder, best_guess_name)

        path = next(
            (p for p in self.state_paths if p.endswith(f"{solution_id}.pkl")),
            None,
        )
        if path is None:
            raise FileNotFoundError(f"State for solution {solution_id} not found.")
        return os.path.join(self.state_folder, path)

    def load_evaluation(self, solution_id: int) -> Evaluation:
        """Load an evaluation from the evaluation file."""
        if self.analysis_mode:
            filename = self._find_evaluation_filename(solution_id)
        else:
            filename = os.path.join(
                self.evaluation_folder,
                f"evaluation_{self.sanitized_current_store_name}_{solution_id}.pkl",
            )
        with open(filename, "rb") as f:
            evaluation = pickle.load(f)
        if Settings.DELETE_LOADED_SOLUTION_ARCHIVES:
            os.remove(filename)
        return evaluation

    def dump_state(self, solution_id: int, state: State) -> None:
        """Dump the current state of the solution dumper to disk."""
        filename = os.path.join(
            self.state_folder,
            f"state_{self.sanitized_current_store_name}_{solution_id}.pkl",
        )
        if (
            os.path.exists(filename)
            and not Settings.OVERWRITE_EXISTING_SOLUTION_ARCHIVES
        ):
            return
        with open(filename, "wb") as f:
            pickle.dump(state, f)

    def load_state(self, solution_id: int) -> State:
        """Load the current state of the solution dumper from disk."""
        if self.analysis_mode:
            filename = self._find_state_filename(solution_id)
        else:
            filename = os.path.join(
                self.state_folder,
                f"state_{self.sanitized_current_store_name}_{solution_id}.pkl",
            )
        with open(filename, "rb") as f:
            state = pickle.load(f)
        if Settings.DELETE_LOADED_SOLUTION_ARCHIVES:
            os.remove(filename)
        return state
