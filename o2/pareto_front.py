from enum import Enum

from o2.models.evaluation import Evaluation
from o2.models.state import State


class FRONT_STATUS(Enum):
    IS_DOMINATED = 1
    DOMINATES = 2
    IN_FRONT = 3


class ParetoFront:
    """A set of solutions, where no solution is dominated by another solution."""

    def __init__(self) -> None:
        self.evaluations: list[Evaluation] = []
        self.states: list[State] = []
        self.removed_solutions: list[Evaluation] = []
        self.removed_states: list[State] = []

    @property
    def size(self) -> int:
        """Return the number of solutions in the front."""
        return len(self.states)

    @property
    def avg_cycle_time(self) -> float:
        """Return the average cycle time of the front."""
        return sum(e.avg_cycle_time for e in self.evaluations) / self.size

    @property
    def avg_cost(self) -> float:
        """Return the average cost of the front."""
        return sum(e.avg_cost for e in self.evaluations) / self.size

    def add(self, evaluation: Evaluation, state: State) -> None:
        """Add a new solution to the front.

        Note, that this does not check if the solution is dominated by any
        other solution. This should be done before calling this method.
        """
        # Remove all solutions dominated by the new solution
        for e, s in zip(self.evaluations, self.states):
            if e.is_dominated_by(evaluation):
                self.evaluations.remove(e)
                self.states.remove(s)
                self.removed_solutions.append(e)
                self.removed_states.append(s)

        self.evaluations.append(evaluation)
        self.states.append(state)

    def is_in_front(self, evaluation: Evaluation) -> FRONT_STATUS:
        """Check whether the evaluation is in front of the current front.

        Returns IS_DOMINATED if the front is dominated by the evaluation
        Returns DOMINATES if the front dominates the evaluation
        Returns IN_FRONT if the evaluation is in the front
        """
        if not self.evaluations:
            return FRONT_STATUS.IN_FRONT

        self_is_always_dominated = True
        for e in self.evaluations:
            if not e.is_dominated_by(evaluation):
                self_is_always_dominated = False
            if evaluation.is_dominated_by(e):
                return FRONT_STATUS.DOMINATES
        if self_is_always_dominated:
            return FRONT_STATUS.IS_DOMINATED
        return FRONT_STATUS.IN_FRONT

    def is_dominated_by(self, evaluation: Evaluation) -> bool:
        """Check whether the evaluation is dominated by the current front."""
        return all(e.is_dominated_by(evaluation) for e in self.evaluations)
