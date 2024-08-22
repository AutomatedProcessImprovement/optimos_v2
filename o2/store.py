from dataclasses import replace
from typing import TYPE_CHECKING, TypeAlias

from o2.models.constraints import ConstraintsType
from o2.models.evaluation import Evaluation
from o2.models.settings import Settings
from o2.models.state import State
from o2.pareto_front import FRONT_STATUS, ParetoFront

if TYPE_CHECKING:
    from o2.actions.base_action import BaseAction

ActionTry: TypeAlias = tuple[FRONT_STATUS, Evaluation, State, "BaseAction"]


class Store:
    """The Store class is the main class that holds the state of the application.

    It holds the current state, the constraints, the previous actions and states,
    the Pareto Fronts, the Tabu List and the Settings.
    """

    def __init__(self, state: State, constraints: ConstraintsType) -> None:
        self.state = state
        self.constraints = constraints

        self.previous_actions: list[BaseAction] = []
        self.previous_states: list[State] = []
        self.pareto_fronts: list[ParetoFront] = []

        self.tabu_list: list[BaseAction] = []

        self.settings: Settings = Settings()

    @property
    def current_pareto_front(self) -> ParetoFront:
        """Returns the current Pareto Front.

        If there is no Pareto Front, creates a new one and returns it.
        """
        if not self.pareto_fronts:
            self.pareto_fronts = [ParetoFront()]
        return self.pareto_fronts[-1]

    @property
    def base_evaluation(self) -> Evaluation:
        """Returns the base evaluation, e.g. the fist evaluation with no changes."""
        return self.pareto_fronts[0].evaluations[0]

    @property
    def current_fastest_evaluation(self):
        if (len(self.current_pareto_front.evaluations)) == 0:
            raise ValueError("No Base Evaluation found in Pareto Front")
        return min(
            # TODO Waiting Time ?
            self.current_pareto_front.evaluations,
            key=lambda x: x.total_cycle_time,
        )

    @property
    def current_timetable(self):
        return self.state.timetable

    def apply_action(self, action: "BaseAction"):
        self.previous_actions.append(action)
        self.previous_states.append(self.state)
        self.state = action.apply(self.state)

    def undo_action(self):
        self.state = self.previous_states.pop()
        self.tabu_list.append(self.previous_actions.pop())

    def process_many_action_tries(
        self, evaluations: list[ActionTry]
    ) -> tuple[list[ActionTry], list[ActionTry]]:
        """Process a list of action evaluations.

        Ignores the evaluations that are dominated by the current Pareto Front.
        Returns two lists, one with the chosen actions and one with the not chosen actions.

        This is useful if multiple actions are evaluated at once.
        """
        chosen_tries = []
        not_chosen_tries = []
        for action_try in evaluations:
            status, evaluation, new_state, action = action_try
            status = self.current_pareto_front.is_in_front(evaluation)
            if status == FRONT_STATUS.IN_FRONT:
                chosen_tries.append(action_try)
                self.previous_actions.append(action)
                self.current_pareto_front.add(evaluation, new_state)
            elif status == FRONT_STATUS.IS_DOMINATED:
                chosen_tries.append(action_try)
                self.previous_actions.append(action)
                self.pareto_fronts.append(ParetoFront())
                self.current_pareto_front.add(evaluation, new_state)
                self.reset_tabu_list()
            else:
                self.tabu_list.append(action)
                not_chosen_tries.append(action_try)
        return chosen_tries, not_chosen_tries

    def evaluate(self) -> tuple[Evaluation, FRONT_STATUS]:
        """Evaluate the current state and add it to the Pareto Front."""
        evaluation = self.state.evaluate(self.settings.show_simulation_errors)
        status = self.current_pareto_front.is_in_front(evaluation)
        if status == FRONT_STATUS.IN_FRONT:
            self.current_pareto_front.add(evaluation, self.state)
        elif status == FRONT_STATUS.IS_DOMINATED:
            self.pareto_fronts.append(ParetoFront())
            self.current_pareto_front.add(evaluation, self.state)

        return evaluation, status

    def reset_tabu_list(self):
        self.tabu_list = []

    # Tries an action and returns the status of the new evaluation
    # Does NOT modify the store
    def tryAction(self, action: "BaseAction") -> ActionTry:
        new_state = action.apply(self.state, enable_prints=False)
        evaluation = new_state.evaluate()
        status = self.current_pareto_front.is_in_front(evaluation)
        return (status, evaluation, new_state, action)

    def replaceConstraints(self, /, **changes):
        self.constraints = replace(self.constraints, **changes)
        return self.constraints

    def replaceState(self, /, **changes):
        self.state = replace(self.state, **changes)
        return self.state

    def replaceTimetable(self, /, **changes):
        self.state = self.state.replace_timetable(**changes)
        return self.state.timetable

    def is_tabu(self, action: "BaseAction"):
        return action in self.tabu_list
