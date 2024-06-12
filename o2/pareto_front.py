from enum import Enum
from o2.types.evaluation import Evaluation
from o2.types.state import State


class FRONT_STATUS(Enum):
    IS_DOMINATED = 1
    DOMINATES = 2
    IN_FRONT = 3


class ParetoFront:
    evaluations: list[Evaluation] = []
    states: list[State] = []

    def add(self, evaluation: Evaluation, state: State):
        self.evaluations.append(evaluation)
        self.states.append(state)

    # Returns whether the evaluation is in front of the current front
    # Returns IS_DOMINATED if the evaluation is dominated by any of the evaluations in the front
    # Returns DOMINATES if the evaluation dominates all of the evaluations in the front
    def is_in_front(self, evaluation: Evaluation):
        self_is_always_dominated = True
        for e in self.evaluations:
            if not e.is_dominated_by(evaluation):
                self_is_always_dominated = False
            if evaluation.is_dominated_by(e):
                return FRONT_STATUS.DOMINATES
        if self_is_always_dominated:
            return FRONT_STATUS.IS_DOMINATED
        return FRONT_STATUS.IN_FRONT

    def is_dominated_by(self, evaluation: Evaluation):
        return all(e.is_dominated_by(evaluation) for e in self.evaluations)
