import functools
import math
from dataclasses import dataclass, field
from json import dumps
from typing import Optional

from o2.actions.base_actions.base_action import BaseAction
from o2.models.evaluation import Evaluation
from o2.models.settings import Settings
from o2.models.state import State
from o2.util.helper import hash_int
from o2.util.solution_dumper import SolutionDumper


@dataclass(frozen=True)
class Solution:
    """A solution in the optimization process.

    A solution is a pair of an evaluation, the (new) state, the old,
    parent state, and the actions that led to this solution. With the last
    action being the one that led to this solution.

    NOTE: There are two evaluations defined in the class, with `evaluation` definiton
    just beeing there to satisfy type checking. The actual evaluation is stored in
    `_evaluation`, which is loaded from the evaluation file when needed.
    """

    actions: list["BaseAction"] = field(default_factory=list)
    """Actions taken since the base state."""

    evaluation: Evaluation  # type: ignore
    _evaluation: Optional[Evaluation] = field(init=False, repr=False, default=None)

    @property
    def evaluation(self) -> Evaluation:
        """Return the evaluation of the solution."""
        if (
            self._evaluation is None
            and "evaluation" in self.__dict__
            and self.__dict__["evaluation"] is not None
        ):
            self.__dict__["_evaluation"] = self.__dict__["evaluation"]
            return self.__dict__["_evaluation"]
        elif self._evaluation is None and Settings.ARCHIVE_SOLUTIONS:
            self.__dict__["_evaluation"] = SolutionDumper.instance.load_evaluation(
                self.id
            )
        assert self._evaluation is not None
        return self._evaluation

    @evaluation.setter
    def evaluation(self, value: Evaluation) -> None:
        """Set the evaluation of the solution."""
        self.__dict__["_evaluation"] = value

    state: State  # type: ignore
    _state: Optional[State] = field(init=False, repr=False, default=None)

    @property
    def state(self) -> State:
        """Return the state of the solution."""
        if self._state is None and Settings.ARCHIVE_SOLUTIONS:
            self.__dict__["_state"] = SolutionDumper.instance.load_state(self.id)
        assert self._state is not None
        return self._state

    @state.setter
    def state(self, value: State) -> None:
        """Set the state of the solution."""
        self.__dict__["_state"] = value

    @property
    def is_base_solution(self) -> bool:
        """Check if this state is the base solution."""
        return not self.actions

    @property
    def last_action(self) -> "BaseAction":
        """Return the last action taken."""
        return self.actions[-1]

    @functools.cached_property
    def point(self) -> tuple[float, float]:
        """Return the evaluation as a point."""
        return self.evaluation.to_tuple()

    @functools.cached_property
    def pareto_x(self) -> float:
        """Return the pareto x of the solution."""
        return self.evaluation.pareto_x

    @functools.cached_property
    def pareto_y(self) -> float:
        """Return the pareto y of the solution."""
        return self.evaluation.pareto_y

    def distance_to(self, other: "Solution") -> float:
        """Calculate the euclidean distance between two evaluations."""
        return math.sqrt(
            (self.pareto_x - other.pareto_x) ** 2
            + (self.pareto_y - other.pareto_y) ** 2
        )

    def is_dominated_by(self, solution: "Solution") -> bool:
        """Check if this solution is dominated by the given solution."""
        return self.evaluation.is_dominated_by(solution.evaluation)

    def has_equal_point(self, solution: "Solution") -> bool:
        """Check if this solution has the same point as the given solution."""
        return self.point == solution.point

    def archive(self) -> None:
        """Archive the solution."""
        if not Settings.ARCHIVE_SOLUTIONS:
            return
        # Solution is already archived
        if self._evaluation is not None:
            SolutionDumper.instance.dump_evaluation(self.id, self.evaluation)
            self.__dict__["_evaluation"] = None
        if self._state is not None:
            SolutionDumper.instance.dump_state(self.id, self.state)
            self.__dict__["_state"] = None

    def __eq__(self, value: object) -> bool:
        """Check if this solution is equal to the given object."""
        if not isinstance(value, Solution):
            return False
        return self.id == value.id

    @functools.cached_property
    def is_valid(self) -> bool:
        """Check if the evaluation is valid."""
        return (
            not self.evaluation.is_empty
            # Ensure that there was no error runing the simulation,
            # that results in a < 1 value.
            and self.pareto_x >= 1
            and self.pareto_y >= 1
        )

    @functools.cached_property
    def id(self) -> int:
        """A unique identifier for the solution.

        Generated only based on the actions.
        """
        return Solution.hash_action_list(self.actions)

    @staticmethod
    def hash_action_list(actions: list["BaseAction"]) -> int:
        """Hash a list of actions."""
        if not actions:
            return 0
        return hash_int(dumps([a.id for a in actions]))

    @staticmethod
    def from_parent(parent: "Solution", action: "BaseAction") -> "Solution":
        """Create a new solution from a parent solution.

        Will automatically apply the action to the parent state,
        and evaluate the new state.
        """
        new_state = action.apply(parent.state, enable_prints=False)
        # If the action did not change the state, we mark the solution as invalid/empty
        # This is due to the fact that many actions will not change the state, if
        # the action is not valid.
        if new_state == parent.state:
            return Solution.empty_from_parent(parent, action)
        evaluation = new_state.evaluate()
        return Solution(
            evaluation=evaluation,
            state=new_state,
            actions=parent.actions + [action],
        )

    @staticmethod
    def empty(state: State, last_action: Optional["BaseAction"] = None) -> "Solution":
        """Create an empty solution."""
        return Solution(
            evaluation=Evaluation.empty(),
            state=state,
            actions=[last_action] if last_action else [],
        )

    @staticmethod
    def empty_from_parent(
        parent: "Solution", last_action: Optional["BaseAction"] = None
    ) -> "Solution":
        """Create an empty solution from a parent solution."""
        return Solution(
            evaluation=Evaluation.empty(),
            state=parent.state,
            actions=parent.actions + [last_action] if last_action else parent.actions,
        )
