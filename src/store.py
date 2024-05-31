from dataclasses import dataclass
from src.pareto_front import FRONT_STATUS, ParetoFront
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
    previous_pareto_fronts: list[ParetoFront] = []

    tabu_list: list[Action] = []

    @property
    def current_pareto_front(self):
        if not self.previous_pareto_fronts:
            self.previous_pareto_fronts = [ParetoFront()]
        return self.previous_pareto_fronts[-1]

    @property
    def base_evaluation(self):
        return self.previous_pareto_fronts[0].evaluations[0]

    def apply_action(self, action: Action):
        self.previous_actions.append(action)
        self.previous_states.append(self.state)
        self.state = action.apply(self.state)

    def undo_action(self):
        self.state = self.previous_states.pop()
        self.tabu_list.append(self.previous_actions.pop())

    def evaluate(self):
        evaluation = self.state.evaluate()
        status = self.current_pareto_front.is_in_front(evaluation)
        if status == FRONT_STATUS.IN_FRONT:
            self.current_pareto_front.add(evaluation, self.state)
        elif status == FRONT_STATUS.DOMINATES:
            self.previous_pareto_fronts.append(ParetoFront())
            self.current_pareto_front.add(evaluation, self.state)

        return evaluation, status

    def reset_tabu_list(self):
        self.tabu_list = []
