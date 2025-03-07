from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Optional

from o2.actions.base_actions.base_action import BaseAction, RateSelfReturnType
from o2.actions.batching_actions.add_date_time_rule_by_availability_action import (
    AddDateTimeRuleByAvailabilityAction,
)
from o2.actions.batching_actions.add_date_time_rule_by_enablement_action import (
    AddDateTimeRuleByEnablementAction,
)
from o2.actions.batching_actions.add_date_time_rule_by_start_action import (
    AddDateTimeRuleByStartAction,
)
from o2.actions.batching_actions.add_large_wt_rule_by_idle_action import (
    AddLargeWTRuleByIdleAction,
)
from o2.actions.batching_actions.add_large_wt_rule_by_wt_action import AddLargeWTRuleByWTAction
from o2.actions.batching_actions.add_ready_wt_rule_by_wt_action import AddReadyWTRuleByWTAction
from o2.actions.batching_actions.modify_daily_hour_rule_action import (
    ModifyDailyHourRuleAction,
)
from o2.actions.batching_actions.modify_size_rule_by_allocation_action import (
    ModifySizeRuleByHighAllocationAction,
    ModifySizeRuleByLowAllocationAction,
)
from o2.actions.batching_actions.modify_size_rule_by_cost_action import (
    ModifySizeRuleByCostAction,
)
from o2.actions.batching_actions.modify_size_rule_by_cost_fn_action import (
    ModifyBatchSizeIfNoCostImprovementAction,
    ModifySizeRuleByCostFnHighCostsAction,
    ModifySizeRuleByCostFnLowCycleTimeImpactAction,
    ModifySizeRuleByCostFnLowProcessingTimeAction,
    ModifySizeRuleByCostFnRepetitiveTasksAction,
    ModifySizeRuleByManySimilarEnablementsAction,
)
from o2.actions.batching_actions.modify_size_rule_by_duration_fn_action import (
    ModifyBatchSizeIfNoDurationImprovementAction,
    ModifySizeRuleByDurationFnCostImpactAction,
)
from o2.actions.batching_actions.modify_size_rule_by_utilization_action import (
    ModifySizeRuleByHighUtilizationAction,
    ModifySizeRuleByLowUtilizationAction,
)
from o2.actions.batching_actions.modify_size_rule_by_wt_action import (
    ModifySizeRuleByWTAction,
)
from o2.actions.batching_actions.random_action import RandomAction
from o2.actions.batching_actions.remove_rule_action import RemoveRuleAction
from o2.actions.deprecated_actions.add_week_day_rule_action import AddWeekDayRuleAction
from o2.actions.deprecated_actions.modify_large_wt_rule_action import (
    ModifyLargeWtRuleAction,
)
from o2.actions.deprecated_actions.modify_ready_wt_rule_action import (
    ModifyReadyWtRuleAction,
)
from o2.actions.legacy_optimos_actions.add_resource_action import AddResourceAction
from o2.actions.legacy_optimos_actions.modify_calendar_by_cost_action import (
    ModifyCalendarByCostAction,
)
from o2.actions.legacy_optimos_actions.modify_calendar_by_it_action import (
    ModifyCalendarByITAction,
)
from o2.actions.legacy_optimos_actions.modify_calendar_by_wt_action import (
    ModifyCalendarByWTAction,
)
from o2.actions.legacy_optimos_actions.remove_resource_by_cost_action import (
    RemoveResourceByCostAction,
)
from o2.actions.legacy_optimos_actions.remove_resource_by_utilization_action import (
    RemoveResourceByUtilizationAction,
)
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.solution import Solution
from o2.store import SolutionTry, Store
from o2.util.indented_printer import print_l1, print_l2

ACTION_CATALOG: list[type[BaseAction]] = [
    AddResourceAction,
    AddWeekDayRuleAction,
    ModifyCalendarByCostAction,
    ModifyCalendarByITAction,
    ModifyCalendarByWTAction,
    ModifyDailyHourRuleAction,
    ModifyLargeWtRuleAction,
    ModifyReadyWtRuleAction,
    RemoveResourceByCostAction,
    RemoveResourceByUtilizationAction,
    RemoveRuleAction,
]


ACTION_CATALOG_LEGACY: list[type[BaseAction]] = [
    AddResourceAction,
    ModifyCalendarByCostAction,
    ModifyCalendarByITAction,
    ModifyCalendarByWTAction,
    RemoveResourceByCostAction,
    RemoveResourceByUtilizationAction,
]

ACTION_CATALOG_BATCHING_ONLY: list[type[BaseAction]] = [
    AddDateTimeRuleByAvailabilityAction,
    AddDateTimeRuleByEnablementAction,
    AddDateTimeRuleByStartAction,
    AddLargeWTRuleByIdleAction,
    AddLargeWTRuleByWTAction,
    AddReadyWTRuleByWTAction,
    ModifyBatchSizeIfNoCostImprovementAction,
    ModifyBatchSizeIfNoDurationImprovementAction,
    ModifySizeRuleByCostAction,
    ModifySizeRuleByCostFnHighCostsAction,
    ModifySizeRuleByCostFnLowCycleTimeImpactAction,
    ModifySizeRuleByCostFnLowProcessingTimeAction,
    ModifySizeRuleByCostFnRepetitiveTasksAction,
    ModifySizeRuleByDurationFnCostImpactAction,
    ModifySizeRuleByHighAllocationAction,
    ModifySizeRuleByHighUtilizationAction,
    ModifySizeRuleByLowAllocationAction,
    ModifySizeRuleByLowUtilizationAction,
    ModifySizeRuleByManySimilarEnablementsAction,
    ModifySizeRuleByWTAction,
    # Legacy Rules, that are fallbacks now
    ModifyDailyHourRuleAction,
    RemoveRuleAction,
]


ACTION_CATALOG_RANDOM: list[type[BaseAction]] = [RandomAction]


class NoNewBaseSolutionFoundError(Exception):
    """Exception raised when no new base solution is found."""

    pass


class NoActionsLeftError(Exception):
    """Exception raised when no actions are left to perform."""

    pass


class Agent(ABC):
    """Selects the best action to take next, based on the current state of the store."""

    def __init__(self, store: Store) -> None:
        super().__init__()
        self.store = store
        self.catalog = (
            ACTION_CATALOG_LEGACY
            if store.settings.optimos_legacy_mode
            else ACTION_CATALOG_BATCHING_ONLY
            if store.settings.batching_only
            else ACTION_CATALOG
        )
        self.action_generators: list[RateSelfReturnType[BaseAction]] = []
        self.action_generator_tabu_ids: set[str] = set()
        self.action_generator_counter: dict[RateSelfReturnType[BaseAction], int] = defaultdict(int)
        self.set_action_generators(store.solution)

    def select_actions(self) -> Optional[list[BaseAction]]:
        """Select the best actions to take next.

        It will pick at most cpu_count actions, so parallel evaluation is possible.

        If the possible options for the current base evaluation are exhausted,
        it will choose a new base evaluation.
        """
        while True:
            print_l1(f"Choosing best action (based on {self.store.solution.id})...")

            # Get valid actions from the generators, even multiple per generator,
            # if we don't have enough valid actions yet
            possible_actions = self.get_valid_actions()
            # Remove None values
            possible_actions = [action for action in possible_actions if action is not None]

            if len(possible_actions) == 0:
                print_l1("No actions remaining, after removing Tabu & N/A actions.")
                new_solution = self.find_new_base_solution(
                    # Setting proposed_solution_try to None, we make sure that
                    # the current solution is not reinserted into the solution tree
                    proposed_solution_try=None
                )
                success = new_solution is not None
                if not success:
                    print_l2("No new baseline evaluation found. Stopping.")
                    return None
                self.store.solution = new_solution
                continue

            sorted_actions = sorted(possible_actions, key=lambda x: x[0], reverse=True)

            number_of_actions_to_select = self.store.settings.max_number_of_actions_per_iteration
            selected_actions = sorted_actions[:number_of_actions_to_select]
            avg_rating = sum(rating for rating, _ in selected_actions) / len(selected_actions)

            print_l1(
                f"Chose {len(selected_actions)} actions with average rating {avg_rating:.1f} to evaluate."  # noqa: E501
            )

            if self.store.settings.print_chosen_actions:
                for rating, action in selected_actions:
                    print_l2(f"{action} with rating {rating}")

            return [action for _, action in selected_actions]

    def get_valid_actions(self) -> list[tuple[RATING, BaseAction]]:
        """Get settings.number_of_actions_to_select valid actions from the generators.

        If an action has already been selected for this iteration, it will skip it.
        If the action is tabu, it will skip it and try the next one.
        If the action is not applicable, it will not try more


        It will take into account the `settings.only_allow_low_last` setting,
        to first select non RATING.LOW actions first.

        NOTE: This function will modify the generators_queue, so it's important
        so think about possible side effects.
        """
        actions: list[tuple[RATING, BaseAction]] = []
        low_actions: list[tuple[RATING, BaseAction]] = []

        while len(self.action_generators) > 0:
            action_generator = self.action_generators.pop(0)
            if isinstance(action_generator, tuple):
                continue

            for rating, action in action_generator:
                if rating == RATING.NOT_APPLICABLE or action is None:
                    break
                if action.id in self.action_generator_tabu_ids:
                    continue
                if self.store.is_tabu(action):
                    self.action_generator_tabu_ids.add(action.id)
                    continue
                if not self.store.settings.disable_action_validity_check and not action.check_if_valid(
                    self.store, mark_no_change_as_invalid=True
                ):
                    self.action_generator_tabu_ids.add(action.id)
                    continue
                if self.store.settings.only_allow_low_last and rating <= RATING.LOW:
                    low_actions.append((rating, action))
                    self.action_generator_tabu_ids.add(action.id)
                    self.action_generator_counter[action_generator] += 1
                else:
                    actions.append((rating, action))
                    self.action_generator_tabu_ids.add(action.id)
                    self.action_generator_counter[action_generator] += 1
                if len(actions) >= self.store.settings.max_number_of_actions_per_iteration:
                    self.action_generators.append(action_generator)
                    return actions
                # If the action generator has yielded more than the max,
                # do not re-add it, thereby forbidding it to yield more
                if (
                    self.store.settings.MAX_YIELDS_PER_ACTION is not None
                    and self.action_generator_counter[action_generator]
                    >= self.store.settings.MAX_YIELDS_PER_ACTION
                ):
                    break

                self.action_generators.append(action_generator)
                break
        if len(actions) == 0:
            return low_actions
        return actions

    def set_action_generators(self, solution: Solution) -> None:
        """Set the action generators for the given solution.

        NOTE: This function **must** be called when setting a new base solution.
        """
        rating_input = SelfRatingInput.from_base_solution(solution)
        self.action_generator_tabu_ids = set()
        self.action_generator_counter = defaultdict(int)
        self.action_generators = [Action.rate_self(self.store, rating_input) for Action in self.catalog]

    def process_many_solutions(
        self, solutions: list[Solution]
    ) -> tuple[list[SolutionTry], list[SolutionTry]]:
        """Process a list of solutions.

        See Store.process_many_solutions for more information.
        """
        chosen_tries, not_chosen_tries = self.store.process_many_solutions(
            solutions,
            self.set_new_base_solution if not self.store.settings.never_select_new_base_solution else None,
        )

        self.result_callback(chosen_tries, not_chosen_tries)
        return chosen_tries, not_chosen_tries

    def set_new_base_solution(self, proposed_solution_try: Optional[SolutionTry] = None) -> None:
        """Set a new base solution."""
        print_l2(f"Selecting new base evaluation {'(reinserting)' if proposed_solution_try else ''}...")
        solution = self.find_new_base_solution(proposed_solution_try)
        if solution != self.store.solution:
            self.set_action_generators(solution)
        self.store.solution = solution

    def try_solution(self, solution: Solution) -> SolutionTry:
        """Try a solution and return the result."""
        return self.store.try_solution(solution)

    @abstractmethod
    def find_new_base_solution(self, proposed_solution_try: Optional[SolutionTry] = None) -> Solution:
        """Select a new base solution.

        E.g from the SolutionTree.

        If proposed_solution_try is None, than the current solution is not
        reinserted into the solution tree, as it's assumed that the function
        was called outside of the normal optimization loop. (E.g. when running out of
        actions)
        If it's not None, than this proposed_solution_try **may** be used as
        the new base solution, but this depends on the Agent implementation.

        NOTE: This function will update the store.solution attribute.
        """
        pass

    @abstractmethod
    def result_callback(self, chosen_tries: list[SolutionTry], not_chosen_tries: list[SolutionTry]) -> None:
        """Handle the result of the evaluation with this callback."""
        pass
