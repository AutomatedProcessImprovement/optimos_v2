import glob
import os
import pickle
from datetime import datetime
from io import BufferedWriter, TextIOWrapper
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

    def __init__(self) -> None:
        """Initialize the solution dumper.

        Creates a folder with the current date and time, and initializes file handles.
        Also sets the singleton instance.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
        self.folder = os.path.join("stores", f"run_{timestamp}")
        self.evaluation_folder = os.path.join(self.folder, "evaluations")
        self.state_folder = os.path.join(self.folder, "states")
        os.makedirs(self.folder, exist_ok=True)
        os.makedirs(self.evaluation_folder, exist_ok=True)
        os.makedirs(self.state_folder, exist_ok=True)

        # Filenames and file handles (initialized later)
        self.current_store_name: Optional[str] = None
        self.sanitized_current_store_name: str = ""
        self.store_filename: str = ""
        self.store_file: Optional[BufferedWriter] = None

        # Set singleton instance
        SolutionDumper.instance = self

    def update_store_name(self, store_name: str) -> None:
        """Update the store name."""
        self._reset_files(store_name)

    def _reset_files(self, store_name: str) -> None:
        """Close existing files and open new ones based on the new store name."""
        # Close existing files if open.
        self.close()

        # Sanitize the store name for filenames.
        sanitized_name = store_name.replace(" ", "_").lower()
        self.store_filename = os.path.join(self.folder, f"store_{sanitized_name}.pkl")

        self.store_file = open(self.store_filename, "wb")  # noqa: SIM115

        self.current_store_name = store_name
        self.sanitized_current_store_name = sanitized_name

    def dump_store(self, store: "Store") -> None:
        """Dump the current store state to disk."""
        # Reset file handles if the store name has changed.
        if store.name != self.current_store_name or self.store_file is None:
            self._reset_files(store.name)

        # Ensure file handles are available.
        assert self.store_file is not None

        # Dump the store object.
        self.store_file.seek(0)
        pickle.dump(store, self.store_file)
        self.store_file.flush()

    def close(self) -> None:
        """Close any open file handles."""
        if self.store_file is not None:
            self.store_file.close()
            self.store_file = None

    def dump_evaluation(self, solution: "Solution") -> None:
        """Dump an evaluation to the evaluation file."""
        filename = os.path.join(
            self.evaluation_folder,
            f"evaluation_{self.sanitized_current_store_name}_{solution.id}.pkl",
        )
        # As we identify the solution by its id, we don't need to dump the
        # evaluation if it already exists.
        if (
            os.path.exists(filename)
            and not Settings.OVERWRITE_EXISTING_SOLUTION_ARCHIVES
        ):
            return
        log_io(f"Dumping evaluation to {filename}")
        with open(filename, "wb") as f:
            pickle.dump(solution.evaluation, f)

    def load_evaluation(self, solution: "Solution") -> Evaluation:
        """Load an evaluation from the evaluation file."""
        filename = f"evaluation_{self.sanitized_current_store_name}_{solution.id}.pkl"

        full_path = os.path.join(self.evaluation_folder, filename)
        with open(full_path, "rb") as f:
            evaluation = pickle.load(f)
            if Settings.DELETE_LOADED_SOLUTION_ARCHIVES:
                os.remove(filename)

            if (
                "_pareto_x" in solution.__dict__
                and evaluation.pareto_x != solution.pareto_x
            ) or (
                "_pareto_y" in solution.__dict__
                and evaluation.pareto_y != solution.pareto_y
            ):
                raise RuntimeError(
                    f"Evaluation for solution {solution.id} has changed."
                )

        log_io(f"Loaded evaluation from {full_path}")
        return evaluation

    def dump_state(self, solution: "Solution") -> None:
        """Dump the current state of the solution dumper to disk."""
        filename = os.path.join(
            self.state_folder,
            f"state_{self.sanitized_current_store_name}_{solution.id}.pkl",
        )
        if (
            os.path.exists(filename)
            and not Settings.OVERWRITE_EXISTING_SOLUTION_ARCHIVES
        ):
            return
        log_io(f"Dumping state to {filename}")
        with open(filename, "wb") as f:
            pickle.dump(solution.state, f)

    def load_state(self, solution: "Solution") -> State:
        """Load the current state of the solution dumper from disk."""
        filename = f"state_{self.sanitized_current_store_name}_{solution.id}.pkl"
        full_path = os.path.join(self.state_folder, filename)
        with open(full_path, "rb") as f:
            state = pickle.load(f)
            state_hash = hash(state)
            if Settings.DELETE_LOADED_SOLUTION_ARCHIVES:
                os.remove(filename)
            if (
                "_state_hash" in solution.__dict__
                and state_hash != solution.__dict__["_state_hash"]
            ):
                raise RuntimeError(f"State for solution {solution.id} has changed.")

        log_io(f"Loaded state from {full_path}")
        return state
