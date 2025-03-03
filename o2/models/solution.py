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

        # In case this is a pre-archived solution (e.g. from a previous run),
        # we can take the evaluation from __dict__['evaluation']
        if (
            self._evaluation is None
            and "evaluation" in self.__dict__
            and self.__dict__["evaluation"] is not None
        ):
            self.__dict__["_evaluation"] = self.__dict__["evaluation"]
            return self.__dict__["_evaluation"]
        # Else we just load the evaluation from the evaluation file
        elif self._evaluation is None and Settings.ARCHIVE_SOLUTIONS:
            self.__dict__["_evaluation"] = SolutionDumper.instance.load_evaluation(self)
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

        # In case this is a pre-archived solution (e.g. from a previous run),
        # we can take the state from __dict__['state']
        if (
            self._state is None
            and "state" in self.__dict__
            and self.__dict__["state"] is not None
        ):
            self.__dict__["_state"] = self.__dict__["state"]
            return self.__dict__["_state"]
        # Else we just load the state from the state file
        elif self._state is None and Settings.ARCHIVE_SOLUTIONS:
            self.__dict__["_state"] = SolutionDumper.instance.load_state(self)
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

    def is_dominated_by(self, other: "Solution") -> bool:
        """Check if this solution is dominated by the given solution."""
        if not Settings.EQUAL_DOMINATION_ALLOWED:
            return other.pareto_x <= self.pareto_x and other.pareto_y <= self.pareto_y
        return other.pareto_x < self.pareto_x and other.pareto_y < self.pareto_y

    def has_equal_point(self, solution: "Solution") -> bool:
        """Check if this solution has the same point as the given solution."""
        return self.point == solution.point

    def archive(self) -> None:
        """Archive the solution.

        For downwards compatibility, we need to check `__dict__['evaluation']`
        and `__dict__['state']` as well.
        """
        if not Settings.ARCHIVE_SOLUTIONS:
            return
        # Solution is already archived
        if self._evaluation is not None or (
            "evaluation" in self.__dict__ and self.__dict__["evaluation"] is not None
        ):
            # Make sure the computed fields are triggered
            self.pareto_x  # noqa: B018
            self.pareto_y  # noqa: B018
            self.point  # noqa: B018
            SolutionDumper.instance.dump_evaluation(self.id, self.evaluation)
            self.__dict__["_evaluation"] = None
            self.__dict__["evaluation"] = None
        if self._state is not None or (
            "state" in self.__dict__ and self.__dict__["state"] is not None
        ):
            # Make sure the computed fields are triggered
            self.__hash__()  # noqa: B018
            SolutionDumper.instance.dump_state(self.id, self.state)
            self.__dict__["_state"] = None
            # Make sure that the legacy state is removed from __dict__
            self.__dict__["state"] = None
        # If we still got the parent state (from a previous run), we need to remove it
        if "parent_state" in self.__dict__:
            self.__dict__["parent_state"] = None

    def __eq__(self, value: object) -> bool:
        """Check if this solution is equal to the given object."""
        if not isinstance(value, Solution):
            return False
        if Settings.CHECK_FOR_TIMETABLE_EQUALITY:
            return self.__hash__() == value.__hash__()
        return self.id == value.id

    def __hash__(self) -> int:
        """Hash the solution (possibly by id or state).

        Also we cache the hash in a __dict__ field.
        (manually as functools.cached_property does not work with __hash__)
        """
        if Settings.CHECK_FOR_TIMETABLE_EQUALITY:
            if "_state_hash" not in self.__dict__:
                self.__dict__["_state_hash"] = hash(self.state)
            return self.__dict__["_state_hash"]
        return self.id

    @functools.cached_property
    def is_valid(self) -> bool:
        """Check if the evaluation is valid."""
        return (
            # Ensure that there was no error runing the simulation,
            # that results in a <= 0 value.
            # Or that the solution is empty
            self.pareto_x > 0 and self.pareto_y > 0
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
