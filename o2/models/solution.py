import functools
from dataclasses import dataclass, field
from json import dumps
from typing import Optional

from o2.actions.base_actions.base_action import BaseAction
from o2.models.evaluation import Evaluation
from o2.models.state import State
from o2.util.helper import hash_int


@dataclass(frozen=True)
class Solution:
    """A solution in the optimization process.

    A solution is a pair of an evaluation, the (new) state, the old,
    parent state, and the actions that led to this solution. With the last
    action being the one that led to this solution.
    """

    evaluation: Evaluation
    state: State
    parent_state: Optional[State]

    actions: list["BaseAction"] = field(default_factory=list)
    """Actions taken since the base state."""

    def __post_init__(self) -> None:  # noqa: D105
        if not self.id:
            self.id = Solution.hash_action_list(self.actions)  # type: ignore

    @property
    def is_base_solution(self) -> bool:
        """Check if this state is the base solution."""
        return not self.actions

    @property
    def last_action(self) -> "BaseAction":
        """Return the last action taken."""
        return self.actions[-1]

    @property
    def point(self) -> tuple[float, float]:
        """Return the evaluation as a point."""
        return self.evaluation.to_tuple()

    def is_dominated_by(self, solution: "Solution") -> bool:
        """Check if this solution is dominated by the given solution."""
        return self.evaluation.is_dominated_by(solution.evaluation)

    @property
    def is_valid(self) -> bool:
        """Check if the evaluation is valid."""
        return not self.evaluation.is_empty

    @functools.cached_property
    def id(self) -> int:
        """A unique identifier for the solution.

        Generated only based on the actions.
        """
        return Solution.hash_action_list(self.actions)

    @staticmethod
    def hash_action_list(actions: list["BaseAction"]) -> int:
        """Hash a list of actions."""
        return hash_int(dumps([a.id for a in actions]))

    @staticmethod
    def from_parent(parent: "Solution", action: "BaseAction") -> "Solution":
        """Create a new solution from a parent solution.

        Will automatically apply the action to the parent state,
        and evaluate the new state.
        """
        new_state = action.apply(parent.state, enable_prints=False)
        evaluation = new_state.evaluate()
        return Solution(
            evaluation=evaluation,
            state=new_state,
            parent_state=parent.state,
            actions=parent.actions + [action],
        )

    @staticmethod
    def empty(state: State) -> "Solution":
        """Create an empty solution."""
        return Solution(
            evaluation=Evaluation.empty(),
            state=state,
            parent_state=None,
            actions=[],
        )
