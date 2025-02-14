import os
import pickle
from datetime import datetime
from io import BufferedWriter, TextIOWrapper
from typing import TYPE_CHECKING, Optional

from o2.models.solution import Solution

if TYPE_CHECKING:
    from o2.store import Store


class SolutionDumper:
    """Helper class to dump solutions and store state to disk for backup purposes."""

    instance: "SolutionDumper"

    def __init__(
        self,
    ) -> None:
        """Initialize the solution dumper.

        Will create a folder with the current date and time, and store the store and solutions in it.
        Also initalizes the singleton instance.
        """
        # Create folder name with timestamp
        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.folder = f"stores/run_{date_str}"
        self.current_store_name = None
        self.solutions_filename: str
        self.store_filename: str
        self.store_stats_filename: str
        # Create folder if it doesn't exist
        os.makedirs(self.folder, exist_ok=True)
        # Open files for writing store and solutions
        self.store_file: Optional[BufferedWriter] = None
        self.store_stats_file: Optional[TextIOWrapper] = None
        self.solutions_file: Optional[BufferedWriter] = None
        SolutionDumper.instance = self

    def dump_solution(self, solution: Solution) -> None:
        """Dump a solution to the solutions file."""
        if self.solutions_file is None:
            self.solutions_file = open(self.solutions_filename, "ab")  # noqa: SIM115
        pickle.dump(solution, self.solutions_file)
        self.solutions_file.flush()

    def dump_store(self, store: "Store") -> None:
        """Dump the current store state to the store file."""
        if store.name != self.current_store_name:
            if self.store_file is not None:
                self.store_file.close()
            if self.store_stats_file is not None:
                self.store_stats_file.close()
            if self.solutions_file is not None:
                self.solutions_file.close()
            sanitized_name = store.name.replace(" ", "_").lower()
            self.store_filename = f"{self.folder}/store_{sanitized_name}.pkl"
            self.store_stats_filename = (
                f"{self.folder}/store_{sanitized_name}_stats.txt"
            )
            self.solutions_filename = f"{self.folder}/solutions_{sanitized_name}.pkl"
            self.store_file = open(self.store_filename, "wb")  # noqa: SIM115
            self.store_stats_file = open(self.store_stats_filename, "w")  # noqa: SIM115
            self.solutions_file = open(self.solutions_filename, "ab")  # noqa: SIM115
            self.current_store_name = store.name
        assert self.store_file is not None
        assert self.store_stats_file is not None
        assert self.solutions_file is not None

        self.store_file.seek(0)
        pickle.dump(store, self.store_file)
        self.store_file.flush()

        self.store_stats_file.seek(0)
        self.store_stats_file.writelines(
            [
                "Current Batching Rules:\n",
                store.current_timetable.batching_rules_debug_str(),
                "\n",
                "\n",
                "All Actions:\n",
                "\n".join(
                    [
                        f"{i}:\t{repr(action)}"
                        for i, action in enumerate(reversed(store.solution.actions))
                    ]
                ),
                "\n",
                "\n",
                "Current Timetable:\n",
                store.current_timetable.to_json(),
            ]
        )
        self.store_stats_file.flush()

    def close(self) -> None:
        """Close the open files."""
        if self.store_file is not None:
            self.store_file.close()
        if self.store_stats_file is not None:
            self.store_stats_file.close()
        if self.solutions_file is not None:
            self.solutions_file.close()

    def load_store(self) -> "Store":
        """Load the store from the store file."""
        with open(self.store_filename, "rb") as f:
            return pickle.load(f)

    def load_solutions(self) -> list[Solution]:
        """Load the solutions from the solutions file."""
        solutions = []
        with open(self.solutions_filename, "rb") as f:
            while True:
                try:
                    solution = pickle.load(f)
                    solutions.append(solution)
                except EOFError:
                    break
        return solutions
