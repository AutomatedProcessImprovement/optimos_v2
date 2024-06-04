from dataclasses import dataclass
from optimos_v2.src.actions.base_action import BaseAction
from src.pareto_front import FRONT_STATUS, ParetoFront

from src.types.constraints import ConstraintsType
from src.types.state import State


class Store:
    def __init__(self, state: State, constraints: ConstraintsType):
        self.state = state
        self.constraints = constraints

    constraints: ConstraintsType
    state: State

    previous_actions: list[BaseAction] = []
    previous_states: list[State] = []
    previous_pareto_fronts: list[ParetoFront] = []

    tabu_list: list[BaseAction] = []

    @property
    def current_pareto_front(self):
        if not self.previous_pareto_fronts:
            self.previous_pareto_fronts = [ParetoFront()]
        return self.previous_pareto_fronts[-1]

    @property
    def base_evaluation(self):
        return self.previous_pareto_fronts[0].evaluations[0]

    @property
    def current_fastest_evaluation(self):
        return sorted(
            self.current_pareto_front.evaluations, key=lambda x: x.total_waiting_time
        )[0]

    def apply_action(self, action: BaseAction):
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
        elif status == FRONT_STATUS.IS_DOMINATED:
            self.previous_pareto_fronts.append(ParetoFront())
            self.current_pareto_front.add(evaluation, self.state)

        return evaluation, status

    def reset_tabu_list(self):
        self.tabu_list = []

    # Tries an action and returns the status of the new evaluation
    # Does NOT modify the store
    def tryAction(self, action: BaseAction):
        new_state = action.apply(self.state, enable_prints=False)
        evaluation = new_state.evaluate()
        status = self.current_pareto_front.is_in_front(evaluation)
        return (status, evaluation, new_state, action)
