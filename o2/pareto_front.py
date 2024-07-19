from enum import Enum

from o2.types.evaluation import Evaluation
from o2.types.state import State


class FRONT_STATUS(Enum):
    IS_DOMINATED = 1
    DOMINATES = 2
    IN_FRONT = 3


class ParetoFront:
    """A set of solutions, where no solution is dominated by another solution."""

    evaluations: list[Evaluation] = []
    states: list[State] = []
    removed_solutions: list[Evaluation] = []
    removed_states: list[State] = []

    def add(self, evaluation: Evaluation, state: State) -> None:
        """Add a new solution to the front.

        Note, that this does not check if the solution is dominated by any
        other solution. This should be done before calling this method.
        """
        # Remove all solutions dominated by the new solution
        dominated_indices = [
            i for i, e in enumerate(self.evaluations) if e.is_dominated_by(evaluation)
        ]
        for i in dominated_indices:
            removed_evaluation = self.evaluations.pop(i)
            removed_state = self.states.pop(i)
            self.removed_solutions.append(removed_evaluation)
            self.removed_states.append(removed_state)

        self.evaluations.append(evaluation)
        self.states.append(state)

    def is_in_front(self, evaluation: Evaluation) -> FRONT_STATUS:
        """Check whether the evaluation is in front of the current front.

        Returns IS_DOMINATED if the front is dominated by the evaluation
        Returns DOMINATES if the front dominates the evaluation
        Returns IN_FRONT if the evaluation is in the front
        """
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
