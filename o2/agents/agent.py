from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Optional

from o2.actions.base_actions.base_action import BaseAction, RateSelfReturnType
from o2.actions.batching_actions.add_date_time_rule_by_availability import (
    AddDateTimeRuleByAvailabilityAction,
)
from o2.actions.batching_actions.add_date_time_rule_by_enablement import (
    AddDateTimeRuleByEnablementAction,
)
from o2.actions.batching_actions.add_date_time_rule_by_start import (
    AddDateTimeRuleByStartAction,
)
from o2.actions.batching_actions.add_large_wt_rule_by_idle import (
    AddLargeWTRuleByIdleAction,
)
from o2.actions.batching_actions.add_large_wt_rule_by_wt import AddLargeWTRuleByWTAction
from o2.actions.batching_actions.add_ready_wt_rule_by_wt import AddReadyWTRuleByWTAction
from o2.actions.batching_actions.modify_daily_hour_rule_action import (
    ModifyDailyHourRuleAction,
)
from o2.actions.batching_actions.modify_size_rule_by_allocation import (
    ModifySizeRuleByHighAllocationAction,
    ModifySizeRuleByLowAllocationAction,
)
from o2.actions.batching_actions.modify_size_rule_by_cost_action import (
    ModifySizeRuleByCostAction,
)
from o2.actions.batching_actions.modify_size_rule_by_cost_fn import (
    ModifyBatchSizeIfNoCostImprovement,
    ModifySizeRuleByCostFnHighCosts,
    ModifySizeRuleByCostFnLowCycleTimeImpact,
    ModifySizeRuleByCostFnLowProcessingTime,
    ModifySizeRuleByCostFnRepetitiveTasks,
    ModifySizeRuleByManySimilarEnablements,
)
from o2.actions.batching_actions.modify_size_rule_by_duration_fn import (
    ModifyBatchSizeIfNoDurationImprovement,
    ModifySizeRuleByDurationFnCostImpact,
)
from o2.actions.batching_actions.modify_size_rule_by_utilization import (
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
from o2.models.self_rating import RATING
from o2.models.solution import Solution
from o2.store import SolutionTry, Store

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
    ModifyBatchSizeIfNoCostImprovement,
    ModifyBatchSizeIfNoDurationImprovement,
    ModifySizeRuleByCostAction,
    ModifySizeRuleByCostFnHighCosts,
    ModifySizeRuleByCostFnLowCycleTimeImpact,
    ModifySizeRuleByCostFnLowProcessingTime,
    ModifySizeRuleByCostFnRepetitiveTasks,
    ModifySizeRuleByDurationFnCostImpact,
    ModifySizeRuleByHighAllocationAction,
    ModifySizeRuleByHighUtilizationAction,
    ModifySizeRuleByLowAllocationAction,
    ModifySizeRuleByLowUtilizationAction,
    ModifySizeRuleByManySimilarEnablements,
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

    @abstractmethod
    def select_actions(self, store: Store) -> Optional[list[BaseAction]]:
        """Select the best actions to take next.

        It will pick at most cpu_count actions, so parallel evaluation is possible.

        If the possible options for the current base evaluation are exhausted,
        it will choose a new base evaluation.
        """
        pass

    @abstractmethod
    def select_new_base_solution(
        self, proposed_solution_try: Optional[SolutionTry] = None
    ) -> Solution:
        """Select a new base solution.

        E.g from the SolutionTree
        """
        pass

    @abstractmethod
    def result_callback(
        self, chosen_tries: list[SolutionTry], not_chosen_tries: list[SolutionTry]
    ) -> None:
        """Handle the result of the evaluation with this callback."""
        pass

    @staticmethod
    def get_valid_actions(
        store: "Store",
        action_generators: list[RateSelfReturnType[BaseAction]],
    ) -> list[tuple[RATING, BaseAction]]:
        """Get settings.number_of_actions_to_select valid actions from the generators.

        If an action has already been selected for this iteration, it will skip it.
        If the action is tabu, it will skip it and try the next one.
        If the action is not applicable, it will not try more


        It will take into account the `settings.only_allow_low_last` setting,
        to first select non RATING.LOW actions first.
        """
        actions: list[tuple[RATING, BaseAction]] = []
        low_actions: list[tuple[RATING, BaseAction]] = []
        ignored_action_ids: set[str] = set()
        generators_queue = action_generators.copy()
        counter: dict[RateSelfReturnType[BaseAction], int] = defaultdict(int)

        while len(generators_queue) > 0:
            action_generator = generators_queue.pop(0)
            if isinstance(action_generator, tuple):
                continue

            for rating, action in action_generator:
                if rating == RATING.NOT_APPLICABLE or action is None:
                    break
                if action.id in ignored_action_ids:
                    continue
                if store.is_tabu(action):
                    ignored_action_ids.add(action.id)
                    continue
                if (
                    not store.settings.disable_action_validity_check
                    and not action.check_if_valid(store, mark_no_change_as_invalid=True)
                ):
                    ignored_action_ids.add(action.id)
                    continue
                if store.settings.only_allow_low_last and rating <= RATING.LOW:
                    low_actions.append((rating, action))
                    ignored_action_ids.add(action.id)
                    counter[action_generator] += 1
                else:
                    actions.append((rating, action))
                    ignored_action_ids.add(action.id)
                    counter[action_generator] += 1
                if len(actions) >= store.settings.max_number_of_actions_to_select:
                    return actions
                # If the action generator has yielded more than the max,
                # do not re-add it, thereby forbidding it to yield more
                if (
                    store.settings.MAX_YIELDS_PER_ACTION is not None
                    and counter[action_generator]
                    >= store.settings.MAX_YIELDS_PER_ACTION
                ):
                    break

                generators_queue.append(action_generator)
                break
        if len(actions) == 0:
            return low_actions
        return actions
