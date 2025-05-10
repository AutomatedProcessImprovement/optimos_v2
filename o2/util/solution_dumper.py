import os
import pickle
from datetime import datetime
from io import BufferedWriter
from typing import TYPE_CHECKING, Optional

from o2.models.evaluation import Evaluation
from o2.models.settings import Settings
from o2.models.state import State
from o2.util.logger import log_io

if TYPE_CHECKING:
    from o2.models.solution import Solution
    from o2.store import Store


class SolutionDumper:
    """Helper class to dump solutions and stores to disk for backup/memory optimization purposes."""

    instance: "SolutionDumper"

    def __init__(self, global_mode: bool = False) -> None:
        """Initialize the solution dumper.

        Creates a folder with the current date and time, and initializes file handles.
        Also sets the singleton instance.

        If global_mode is True, the solution dumper will use the global folders
        for all dumps and switch to a read-only mode. This is used by the
        analysis scripts.
        """
        self.global_mode = global_mode

        # Filenames and file handles (initialized later)
        self.current_store_name: Optional[str] = None
        self.sanitized_current_store_name: str = ""
        self.store_filename: str = ""
        self.store_file: Optional[BufferedWriter] = None
        self.solutions_filename: str = ""
        self.solutions_file: Optional[BufferedWriter] = None

        self.iteration: int = 0

        if self.global_mode:
            log_io("Using global folders to load states and evaluations.")
            self.use_global_folders()
            SolutionDumper.instance = self
            return

        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
        self.folder = os.path.join("stores", f"run_{timestamp}")
        self.evaluation_folder = os.path.join(self.folder, "evaluations")
        self.state_folder = os.path.join(self.folder, "states")

        os.makedirs(self.folder, exist_ok=True)
        os.makedirs(self.evaluation_folder, exist_ok=True)
        os.makedirs(self.state_folder, exist_ok=True)

        log_io(f"Initialized solution dumper in folder: {self.folder}")

        # Set singleton instance
        SolutionDumper.instance = self

    def use_global_folders(self) -> None:
        """Use global folders for all dumps."""
        self.close()

        self.global_mode = True
        self.evaluation_folder = "evaluations/"
        self.state_folder = "states/"

    def update_store_name(self, store_name: str) -> None:
        """Update the store name."""

        log_io(f"Updating store name to: {store_name}")

        self.current_store_name = store_name
        # Sanitize the store name for filenames.
        self.sanitized_current_store_name = self._sanitize_store_name(store_name)

        self._reset_files(store_name)

    def _sanitize_store_name(self, store_name: str) -> str:
        """Sanitize the store name for filenames."""
        return store_name.replace(" ", "_").lower()

    def _reset_files(self, store_name: str) -> None:
        """Close existing files and open new ones based on the new store name."""
        assert not self.global_mode

        # Close existing files if open.
        self.close()

        assert self.sanitized_current_store_name != ""

        self.store_filename = os.path.join(self.folder, f"store_{self.sanitized_current_store_name}.pkl")
        self.solutions_filename = os.path.join(
            self.folder, f"solutions_{self.sanitized_current_store_name}.pkl"
        )

        self.store_file = open(self.store_filename, "wb")  # noqa: SIM115
        self.solutions_file = open(self.solutions_filename, "wb")  # noqa: SIM115

    def dump_store(self, store: "Store") -> None:
        """Dump the current store state to disk."""
        assert not self.global_mode

        # Reset file handles if the store name has changed.
        if store.name != self.current_store_name or self.store_file is None:
            self.update_store_name(store.name)

        # Ensure file handles are available.
        assert self.store_file is not None

        # Write the iteration number to the store
        store.__dict__["_iteration"] = self.iteration

        # Dump the store object.
        self.store_file.seek(0)
        pickle.dump(store, self.store_file)
        self.store_file.flush()

    def dump_solution(self, solution: "Solution") -> None:
        """Dump a solution to the solutions file."""
        assert not self.global_mode

        assert self.solutions_file is not None

        # Make sure, that the solution is archived.
        solution.archive()

        # We write the store name & iteration number into the
        # solution object, so we can identify it later.
        solution.__dict__["_store_name"] = self.current_store_name
        solution.__dict__["_iteration"] = self.iteration

        pickle.dump(solution, self.solutions_file)
        self.solutions_file.flush()

    def dump_evaluation(self, solution: "Solution") -> None:
        """Dump an evaluation to the evaluation file."""
        assert not self.global_mode

        filename = os.path.join(
            self.evaluation_folder,
            f"evaluation_{self.sanitized_current_store_name}_{solution.id}.pkl",
        )
        # As we identify the solution by its id, we don't need to dump the
        # evaluation if it already exists.
        if os.path.exists(filename) and not Settings.OVERWRITE_EXISTING_SOLUTION_ARCHIVES:
            return
        log_io(f"Dumping evaluation to {filename}")
        with open(filename, "wb") as f:
            pickle.dump(solution.evaluation, f)

    def load_evaluation(self, solution: "Solution") -> Evaluation:
        """Load an evaluation from the evaluation file."""

        # If the solution was dumped, it may not be processed in the context
        # of the current store, so we override the store name.
        if "_store_name" in solution.__dict__:
            store_name = solution.__dict__["_store_name"]
        else:
            store_name = self.current_store_name

        assert store_name is not None
        store_name = self._sanitize_store_name(store_name)

        filename = f"evaluation_{store_name}_{solution.id}.pkl"

        full_path = os.path.join(self.evaluation_folder, filename)
        with open(full_path, "rb") as f:
            evaluation = pickle.load(f)
            if Settings.DELETE_LOADED_SOLUTION_ARCHIVES:
                os.remove(filename)

            if ("_pareto_x" in solution.__dict__ and evaluation.pareto_x != solution.pareto_x) or (
                "_pareto_y" in solution.__dict__ and evaluation.pareto_y != solution.pareto_y
            ):
                raise RuntimeError(f"Evaluation for solution {solution.id} has changed.")

        log_io(f"Loaded evaluation from {full_path}")
        return evaluation

    def dump_state(self, solution: "Solution") -> None:
        """Dump the current state of the solution dumper to disk."""
        assert not self.global_mode

        filename = os.path.join(
            self.state_folder,
            f"state_{self.sanitized_current_store_name}_{solution.id}.pkl",
        )
        if os.path.exists(filename) and not Settings.OVERWRITE_EXISTING_SOLUTION_ARCHIVES:
            return
        log_io(f"Dumping state to {filename}")
        with open(filename, "wb") as f:
            pickle.dump(solution.state, f)

    def load_state(self, solution: "Solution") -> State:
        """Load the current state of the solution dumper from disk."""

        # If the solution was dumped, it may not be processed in the context
        # of the current store, so we override the store name.
        if "_store_name" in solution.__dict__:
            store_name = solution.__dict__["_store_name"]
        else:
            store_name = self.current_store_name

        assert store_name is not None
        store_name = self._sanitize_store_name(store_name)

        filename = f"state_{store_name}_{solution.id}.pkl"
        full_path = os.path.join(self.state_folder, filename)
        with open(full_path, "rb") as f:
            state = pickle.load(f)
            timetable_hash = hash(state.timetable)
            if Settings.DELETE_LOADED_SOLUTION_ARCHIVES:
                os.remove(filename)
            if (
                "_timetable_hash" in solution.__dict__
                and timetable_hash != solution.__dict__["_timetable_hash"]
            ):
                raise RuntimeError(f"State for solution {solution.id} has changed.")

        log_io(f"Loaded state from {full_path}")
        return state

    def close(self) -> None:
        """Close any open file handles."""

        if self.store_file is not None:
            self.store_file.close()
            self.store_file = None
        if self.solutions_file is not None:
            self.solutions_file.close()
            self.solutions_file = None
