from dataclasses import replace
from typing import TYPE_CHECKING, Callable, Optional, TypeAlias

from o2.actions.base_actions.modify_calendar_base_action import ModifyCalendarBaseAction
from o2.actions.base_actions.modify_resource_base_action import ModifyResourceBaseAction
from o2.models.constraints import ConstraintsType
from o2.models.evaluation import Evaluation
from o2.models.settings import Settings
from o2.models.solution import Solution
from o2.models.solution_tree import SolutionTree
from o2.models.state import State
from o2.pareto_front import FRONT_STATUS, ParetoFront
from o2.util.indented_printer import print_l2

if TYPE_CHECKING:
    from o2.actions.base_actions.base_action import BaseAction
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

        # This is the base Pareto Front
        self.pareto_fronts: list[ParetoFront] = [ParetoFront()]
        self.pareto_fronts[0].add(solution)

        # Add another Pareto Front for the current iteration
        # We need to do that, as the base solution might otherwise be dominated
        # by a new solution and thereby self.pareto_fronts[0].solutions[0]
        # will be changed.
        self.pareto_fronts.append(ParetoFront())
        self.pareto_fronts[-1].add(solution)

        self.solution_tree = SolutionTree()
        self.solution_tree.add_solution(solution, archive=False)

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

    def mark_action_as_tabu(self, action: "BaseAction") -> None:
        """Mark an action as tabu."""
        solution = Solution(
            evaluation=Evaluation.empty(),
            state=self.solution.state,
            actions=[*self.solution.actions, action],
        )

        self.solution_tree.add_solution(solution)

    def process_many_solutions(
        self,
        solutions: list[Solution],
        set_new_base_evaluation_callback: Optional[Callable[[SolutionTry], None]] = None,
    ) -> tuple[list[SolutionTry], list[SolutionTry]]:
        """Process a list of action solutions.

        Ignores the solutions that are dominated by the current Pareto Front.
        Returns two lists, one with the chosen actions and one with the not chosen actions.

        This is useful if multiple actions are evaluated at once.

        The set_new_base_evaluation_callback is called when a new base potential base_solution
        is found. It's assumed that the callback will update the store.solution attribute.
        """
        chosen_tries = []
        not_chosen_tries = []
        new_baseline_chosen = False
        for solution in solutions:
            status = self.current_pareto_front.is_in_front(solution)

            if solution.is_valid:
                # We directly archive the solutions that are not in the front
                # because we most likely will not need them again.
                should_archive = status != FRONT_STATUS.IN_FRONT and status != FRONT_STATUS.IS_DOMINATED
                self.solution_tree.add_solution(solution, archive=should_archive)
            else:
                # If the solution is invalid, override the status to invalid
                status = FRONT_STATUS.INVALID
                self.solution_tree.add_solution_as_discarded(solution)

            if status == FRONT_STATUS.IN_FRONT:
                chosen_tries.append((status, solution))
                self.current_pareto_front.add(solution)
            elif status == FRONT_STATUS.IS_DOMINATED:
                chosen_tries.append((status, solution))
                self.pareto_fronts.append(ParetoFront())
                self.current_pareto_front.add(solution)
                # A dominating solution, will always override the current baseline
                new_baseline_chosen = False
            else:
                not_chosen_tries.append((status, solution))

            if not new_baseline_chosen and (
                status == FRONT_STATUS.IN_FRONT or status == FRONT_STATUS.IS_DOMINATED
            ):
                if set_new_base_evaluation_callback is not None:
                    set_new_base_evaluation_callback((status, solution))
                else:
                    self.solution = solution
                new_baseline_chosen = True

        return chosen_tries, not_chosen_tries

    def run_action(self, action: "BaseAction") -> Optional[Solution]:
        """Run an action and add the new solution to the store.

        NOTE: Usually you would use the HillClimber to run actions.
        This method should only be used in tests.

        NOTE: This will only update the store if the action is not dominated
        """
        new_solution = Solution.from_parent(self.solution, action)
        self.process_many_solutions([new_solution], None)

    # Tries an action and returns the status of the new evaluation
    # Does NOT modify the store
    def try_solution(self, solution: "Solution") -> SolutionTry:
        """Try an action and return the status of the new evaluation.

        If the evaluation throws an exception, it returns IS_DOMINATED.
        """
        try:
            if not solution.is_valid:
                return (FRONT_STATUS.INVALID, solution)
            status = self.current_pareto_front.is_in_front(solution)
            return (status, solution)
        except Exception as e:
            print_l2(f"Error in try_action: {e}")
            return (FRONT_STATUS.INVALID, solution)

    def is_tabu(self, action: "BaseAction") -> bool:
        """Check if the action is tabu."""
        return self.solution_tree.check_if_already_done(self.solution, action)

    @staticmethod
    def from_state_and_constraints(
        state: State, constraints: ConstraintsType, name: str = "An Optimos Run"
    ) -> "Store":
        """Create a new Store from a state and constraints."""
        updated_state = replace(state, timetable=state.timetable.init_fixed_cost_fns(constraints))
        evaluation = updated_state.evaluate()
        solution = Solution(evaluation=evaluation, state=updated_state, actions=[])
        return Store(solution, constraints, name)
