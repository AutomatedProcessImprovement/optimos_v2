from enum import Enum
from src.types.evaluation import Evaluation
from src.types.state import State


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

    def is_in_front(self, evaluation: Evaluation):
        for e in self.evaluations:
            if e.is_dominated_by(evaluation):
                return FRONT_STATUS.IS_DOMINATED
            if evaluation.is_dominated_by(e):
                return FRONT_STATUS.DOMINATES
        return FRONT_STATUS.IN_FRONT
