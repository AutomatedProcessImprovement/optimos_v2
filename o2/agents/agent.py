from abc import ABC, abstractmethod
from typing import Optional, Type

from o2.actions.add_resource_action import AddResourceAction
from o2.actions.add_week_day_rule_action import AddWeekDayRuleAction
from o2.actions.base_action import BaseAction, RateSelfReturnType
from o2.actions.modify_calendar_by_cost_action import (
    ModifyCalendarByCostAction,
)
from o2.actions.modify_calendar_by_it_action import ModifyCalendarByITAction
from o2.actions.modify_calendar_by_wt_action import ModifyCalendarByWTAction
from o2.actions.modify_daily_hour_rule_action import ModifyDailyHourRuleAction
from o2.actions.modify_large_wt_rule_action import ModifyLargeWtRuleAction
from o2.actions.modify_ready_wt_rule_action import ModifyReadyWtRuleAction
from o2.actions.new_actions.modify_size_rule_by_cost_action import (
    ModifySizeRuleByCostAction,
)
from o2.actions.new_actions.modify_size_rule_by_cost_fn import (
    ModifySizeRuleByCostFnHighCosts,
    ModifySizeRuleByCostFnLowCycleTimeImpact,
    ModifySizeRuleByCostFnRepetitiveTasks,
)
from o2.actions.new_actions.modify_size_rule_by_wt_action import (
    ModifySizeRuleByWTAction,
)
from o2.actions.remove_resource_by_cost_action import (
    RemoveResourceByCostAction,
)
from o2.actions.remove_resource_by_utilization_action import (
    RemoveResourceByUtilizationAction,
)
from o2.actions.remove_rule_action import (
    RemoveRuleAction,
)
from o2.models.self_rating import RATING
from o2.models.solution import Solution
from o2.store import SolutionTry, Store

ACTION_CATALOG: list[Type[BaseAction]] = [
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


ACTION_CATALOG_LEGACY = [
    AddResourceAction,
    ModifyCalendarByCostAction,
    ModifyCalendarByITAction,
    ModifyCalendarByWTAction,
    RemoveResourceByCostAction,
    RemoveResourceByUtilizationAction,
]

ACTION_CATALOG_BATCHING_ONLY = [
    ModifySizeRuleByWTAction,
    ModifySizeRuleByCostAction,
    ModifySizeRuleByCostFnHighCosts,
    ModifySizeRuleByCostFnRepetitiveTasks,
    ModifySizeRuleByCostFnLowCycleTimeImpact,
]


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

    @staticmethod
    def get_valid_actions(
        store: "Store",
        action_generators: list[RateSelfReturnType],
    ) -> list[tuple[RATING, BaseAction]]:
        """Get settings.number_of_actions_to_select valid actions from the generators.

        If the action is tabu, it will skip it and try the next one.
        If the action is not applicable, it will not try more

        It will take into account the `settings.only_allow_low_last` setting,
        to first select non RATING.LOW actions first.
        """
        actions = []
        low_actions = []
        generators_queue = action_generators.copy()

        while len(generators_queue) > 0:
            action_generator = generators_queue.pop(0)
            if isinstance(action_generator, tuple):
                continue

            for rating, action in action_generator:
                if rating == RATING.NOT_APPLICABLE or action is None:
                    break
                if store.is_tabu(action):
                    continue
                if not action.check_if_valid(store):
                    continue
                if store.settings.only_allow_low_last and rating == RATING.LOW:
                    low_actions.append((rating, action))
                else:
                    actions.append((rating, action))
                if len(actions) >= store.settings.max_number_of_actions_to_select:
                    return actions

                generators_queue.append(action_generator)
                break
        if len(actions) == 0:
            return low_actions
        return actions
