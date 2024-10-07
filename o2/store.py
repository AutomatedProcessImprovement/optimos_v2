from dataclasses import replace
from typing import TYPE_CHECKING, Optional, TypeAlias

from o2.actions.modify_calendar_base_action import ModifyCalendarBaseAction
from o2.actions.modify_resource_base_action import ModifyResourceBaseAction
from o2.models.constraints import ConstraintsType
from o2.models.evaluation import Evaluation
from o2.models.settings import Settings
from o2.models.solution import Solution
from o2.models.solution_tree import SolutionTree
from o2.models.state import State
from o2.pareto_front import FRONT_STATUS, ParetoFront

if TYPE_CHECKING:
    from o2.actions.base_action import BaseAction
    from o2.models.timetable import TimetableType

ActionTry: TypeAlias = tuple[FRONT_STATUS, Solution]


class Store:
    """The Store class is the main class that holds the state of the application.

    It holds the current state, the constraints, the previous actions and states,
    the Pareto Fronts, the Tabu List and the Settings.
    """

    def __init__(
        self,
        solution: Solution,
        constraints: ConstraintsType,
        name: str = "An Optimos Run",
    ) -> None:
        self.name = name

        self.constraints = constraints

        self.pareto_fronts: list[ParetoFront] = [ParetoFront()]
        self.pareto_fronts[0].add(solution)

        self.solution_tree = SolutionTree()

        self.solution = solution
        """The current solution of the optimization process.

        It will be updated after any change to the pareto front or after a iteration.
        """

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
    def base_solution(self) -> Solution:
        """Returns the base solution, e.g. the fist solution with no changes."""
        return self.pareto_fronts[0].solutions[0]

    @property
    def base_evaluation(self) -> Evaluation:
        """Returns the base evaluation, e.g. the fist evaluation with no changes."""
        return self.base_solution.evaluation

    @property
    def base_state(self) -> State:
        """Returns the base state, e.g. the state before any changes."""
        return self.base_solution.state

    @property
    def current_evaluation(self) -> Evaluation:
        return self.solution.evaluation

    @property
    def current_timetable(self) -> "TimetableType":
        return self.base_solution.state.timetable

    def choose_new_base_evaluation(self) -> Optional[Solution]:
        """Choose a new base evaluation from the solution tree."""
        new_solution = self.solution_tree.pop_nearest_solution(
            self.current_pareto_front
        )
        if new_solution is None:
            return None

        self.solution = new_solution
        return new_solution

    def _add_solution(self, solution: Solution, dominated_by_front: bool) -> None:
        """Add an action and state to the store."""
        self.solution_tree.add_solution(solution)
        # If we are in legacy optimos combined mode, we need to switch the mode
        if (
            not dominated_by_front
            and self.settings.legacy_approach.combined_enabled
            and isinstance(solution.last_action, ModifyCalendarBaseAction)
            or isinstance(solution.last_action, ModifyResourceBaseAction)
        ):
            self.settings.set_next_combined_mode_status()

        # While it's reasonable to assume that the given solution is a valid next
        # base solution, we will still use choose_new_base_evaluation, as
        # maybe it's still suboptimal to choose the nearest solution.
        self.choose_new_base_evaluation()

    def process_many_action_tries(
        self, solutions: list[Solution]
    ) -> tuple[list[ActionTry], list[ActionTry]]:
        """Process a list of action solutions.

        Ignores the solutions that are dominated by the current Pareto Front.
        Returns two lists, one with the chosen actions and one with the not chosen actions.

        This is useful if multiple actions are evaluated at once.
        """
        chosen_tries = []
        not_chosen_tries = []
        for solution in solutions:
            status = (
                self.current_pareto_front.is_in_front(solution)
                # We need to skip actions not valid by legacy_combined_mode_status
                if not self.settings.legacy_approach.combined_enabled
                or self.settings.legacy_approach.action_matches(solution.last_action)
                else None
            )
            if solution.evaluation.is_empty:
                status = FRONT_STATUS.INVALID

            if status == FRONT_STATUS.IN_FRONT:
                chosen_tries.append((status, solution))
                self.current_pareto_front.add(solution)
                self._add_solution(solution, False)
            elif status == FRONT_STATUS.IS_DOMINATED:
                chosen_tries.append((status, solution))
                self.pareto_fronts.append(ParetoFront())
                self.current_pareto_front.add(solution)
                self._add_solution(solution, False)
            else:
                self._add_solution(solution, True)
                not_chosen_tries.append((status, solution))
        return chosen_tries, not_chosen_tries

    # Tries an action and returns the status of the new evaluation
    # Does NOT modify the store
    def try_action(self, action: "BaseAction") -> ActionTry:
        """Try an action and return the status of the new evaluation.

        If the evaluation throws an exception, it returns IS_DOMINATED.
        """
        try:
            new_solution = Solution.from_parent(self.solution, action)
            if not new_solution.is_valid:
                raise Exception("Evaluation empty. Please check the timetable & model.")
            status = self.current_pareto_front.is_in_front(new_solution)
            return (status, new_solution)
        except Exception as e:
            print(f"Error in try_action: {e}")
            return (FRONT_STATUS.INVALID, Solution.empty(self.solution.state))

    def is_tabu(self, action: "BaseAction") -> bool:
        """Check if the action is tabu."""
        return self.solution_tree.check_if_already_done(self.solution, action)

    @staticmethod
    def from_state_and_constraints(
        state: State, constraints: ConstraintsType
    ) -> "Store":
        """Create a new Store from a state and constraints."""
        evaluation = state.evaluate()
        solution = Solution(evaluation, state, None)
        return Store(solution, constraints)
