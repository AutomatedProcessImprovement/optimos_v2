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

SolutionTry: TypeAlias = tuple[FRONT_STATUS, Solution]


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
        self.solution_tree.add_solution(solution)

        self.solution = solution
        """The current solution of the optimization process.

        It will be updated after any change to the pareto front or after a iteration.
        """

        self.settings: Settings = Settings()

    @property
    def current_pareto_front(self) -> ParetoFront:
        """Returns the current Pareto Front."""
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
    def base_timetable(self) -> "TimetableType":
        """Returns the base timetable, e.g. the timetable before any changes."""
        return self.base_state.timetable

    @property
    def current_evaluation(self) -> Evaluation:
        """Returns the current evaluation of the solution."""
        return self.solution.evaluation

    @property
    def current_timetable(self) -> "TimetableType":
        """Return the current timetable of the solution."""
        return self.solution.state.timetable

    @property
    def current_state(self) -> State:
        """Return the current state of the solution."""
        return self.solution.state

    def choose_new_base_evaluation(
        self, reinsert_current_solution: bool = False
    ) -> Optional[Solution]:
        """Choose a new base evaluation from the solution tree.

        If reinsert_current_solution is True, the current solution will be
        reinserted into the solution tree. This is useful if you aren't
        sure if you exhausted all possible actions for this solution.
        """
        if reinsert_current_solution:
            self.solution_tree.add_solution(self.solution)
        new_solution = self.solution_tree.pop_nearest_solution(
            self.current_pareto_front,
            max_distance=self.settings.max_distance_to_new_base_solution,
        )

        if new_solution is None:
            raise Exception("No new base solutions left in the solution tree.")

        self.solution = new_solution
        return new_solution

    def _add_solution(self, solution: Solution, dominated_by_front: bool) -> None:
        """Add an action and state to the store."""
        self.solution_tree.add_solution(solution)

    def mark_action_as_tabu(self, action: "BaseAction") -> None:
        """Mark an action as tabu."""
        solution = Solution(
            Evaluation.empty(),
            self.solution.state,
            self.solution.state,
            [*self.solution.actions, action],
        )

        self.solution_tree.add_solution(solution)

    def process_many_solutions(
        self, solutions: list[Solution]
    ) -> tuple[list[SolutionTry], list[SolutionTry]]:
        """Process a list of action solutions.

        Ignores the solutions that are dominated by the current Pareto Front.
        Returns two lists, one with the chosen actions and one with the not chosen actions.

        This is useful if multiple actions are evaluated at once.
        """
        chosen_tries = []
        not_chosen_tries = []
        for solution in solutions:
            status = self.current_pareto_front.is_in_front(solution)
            if solution.evaluation.is_empty:
                status = FRONT_STATUS.INVALID

            if status == FRONT_STATUS.IN_FRONT:
                chosen_tries.append((status, solution))
                self.current_pareto_front.add(solution)
                self._add_solution(solution, False)
                if not self.settings.never_select_new_base_solution:
                    # We choose a new base evaluation, to continue with our new front entry
                    self.choose_new_base_evaluation(reinsert_current_solution=True)
                else:
                    self.solution = solution
            elif status == FRONT_STATUS.IS_DOMINATED:
                chosen_tries.append((status, solution))
                self.pareto_fronts.append(ParetoFront())
                self.current_pareto_front.add(solution)
                self._add_solution(solution, False)
                if not self.settings.never_select_new_base_solution:
                    # We choose a new base evaluation, because we are in a new front
                    self.choose_new_base_evaluation(reinsert_current_solution=True)
                else:
                    self.solution = solution
            else:
                self._add_solution(solution, True)
                not_chosen_tries.append((status, solution))
        return chosen_tries, not_chosen_tries

    def run_action(self, action: "BaseAction") -> Optional[Solution]:
        """Run an action and add the new solution to the store.

        NOTE: Usually you would use the HillClimber to run actions.
        This method should only be used in tests.

        NOTE: This will only update the store if the action is not dominated
        """
        new_solution = Solution.from_parent(self.solution, action)
        self.process_many_solutions([new_solution])

    # Tries an action and returns the status of the new evaluation
    # Does NOT modify the store
    def try_solution(self, solution: "Solution") -> SolutionTry:
        """Try an action and return the status of the new evaluation.

        If the evaluation throws an exception, it returns IS_DOMINATED.
        """
        try:
            if not solution.is_valid:
                raise Exception("Evaluation empty. Please check the timetable & model.")
            status = self.current_pareto_front.is_in_front(solution)
            return (status, solution)
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
