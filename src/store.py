from dataclasses import dataclass
from src.actions import Action
from src.types.constraints import ConstraintsType
from src.types.evaluation import Evaluation
from src.types.state import State
from src.types.timetable import TimetableType


class Store:
    def __init__(self, state: State):
        self.state = state

    state: State

    previous_actions: list[Action] = []
    previous_states: list[State] = []
    previous_evaluations: list[Evaluation] = []

    tabu_list: list[Action] = []

    @property
    def current_evaluation(self):
        if not self.previous_evaluations:
            return Evaluation.empty()
        return self.previous_evaluations[-1]

    def apply_action(self, action: Action):
        self.previous_actions.append(action)
        self.previous_states.append(self.state)
        self.state = action.apply(self.state)

    def undo_action(self):
        self.state = self.previous_states.pop()
        self.tabu_list.append(self.previous_actions.pop())

    def evaluate(self):
        evaluation = self.state.evaluate()
        self.previous_evaluations.append(evaluation)
        return evaluation

    def reset_tabu_list(self):
        self.tabu_list = []
