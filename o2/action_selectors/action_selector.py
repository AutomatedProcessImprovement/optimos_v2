from abc import ABC, abstractmethod
from typing import Optional, Type

from o2.actions.add_resource_action import AddResourceAction
from o2.actions.add_week_day_rule_action import AddWeekDayRuleAction
from o2.actions.base_action import BaseAction
from o2.actions.modify_calendar_by_cost_action import (
    ModifyCalendarByCostAction,
)
from o2.actions.modify_calendar_by_it_action import ModifyCalendarByITAction
from o2.actions.modify_calendar_by_wt_action import ModifyCalendarByWTAction
from o2.actions.modify_daily_hour_rule_action import ModifyDailyHourRuleAction
from o2.actions.modify_large_wt_rule_action import ModifyLargeWtRuleAction
from o2.actions.modify_ready_wt_rule_action import ModifyReadyWtRuleAction
from o2.actions.modify_size_rule_action import (
    ModifySizeRuleAction,
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
from o2.store import Store

ACTION_CATALOG: list[Type[BaseAction]] = [
    AddResourceAction,
    AddWeekDayRuleAction,
    ModifyCalendarByCostAction,
    ModifyCalendarByITAction,
    ModifyCalendarByWTAction,
    ModifyDailyHourRuleAction,
    ModifyLargeWtRuleAction,
    ModifyReadyWtRuleAction,
    ModifySizeRuleAction,
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


class ActionSelector(ABC):
    """Selects the best action to take next, based on the current state of the store."""

    @abstractmethod
    def select_actions(self, store: Store) -> Optional[list[BaseAction]]:
        """Select the best actions to take next.

        It will pick at most cpu_count actions, so parallel evaluation is possible.

        If the possible options for the current base evaluation are exhausted,
        it will choose a new base evaluation.
        """
        pass
