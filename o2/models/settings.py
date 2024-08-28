from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from o2.actions.modify_calendar_base_action import ModifyCalendarBaseAction
from o2.actions.modify_resource_base_action import ModifyResourceBaseAction

if TYPE_CHECKING:
    from o2.actions.base_action import BaseAction


class LegacyCombinedModeStatus(str, Enum):
    """The status of the legacy combined mode.

    See Settings.legacy_combined_mode_status for more information.
    """

    ACTIVE_CALENDAR_NEXT = "ACTIVE_CALENDAR_NEXT"
    ACTIVE_RESOURCES_NEXT = "ACTIVE_RESOURCES_NEXT"
    DISABLED = "DISABLED"

    def next(self) -> "LegacyCombinedModeStatus":
        """Get the next status in the cycle."""
        if self == LegacyCombinedModeStatus.ACTIVE_CALENDAR_NEXT:
            return LegacyCombinedModeStatus.ACTIVE_RESOURCES_NEXT
        if self == LegacyCombinedModeStatus.ACTIVE_RESOURCES_NEXT:
            return LegacyCombinedModeStatus.ACTIVE_CALENDAR_NEXT
        return LegacyCombinedModeStatus.DISABLED

    @property
    def enabled(self) -> bool:
        """Return whether the combined mode is enabled."""
        return self != LegacyCombinedModeStatus.DISABLED

    @property
    def calendar_is_next(self) -> bool:
        """Return whether the calendar is next in the combined mode."""
        return self == LegacyCombinedModeStatus.ACTIVE_CALENDAR_NEXT

    @property
    def resource_is_next(self) -> bool:
        """Return whether the resources are next in the combined mode."""
        return self == LegacyCombinedModeStatus.ACTIVE_RESOURCES_NEXT

    def action_matches(self, action: "BaseAction") -> bool:
        """Return whether the action matches the current combined mode status."""
        if self == LegacyCombinedModeStatus.ACTIVE_CALENDAR_NEXT:
            return isinstance(action, ModifyCalendarBaseAction)
        if self == LegacyCombinedModeStatus.ACTIVE_RESOURCES_NEXT:
            return isinstance(action, ModifyResourceBaseAction)
        return False


@dataclass()
class Settings:
    """Settings for the Optimos v2 application.

    This class is initialized with sensible defaults, but can be changed to
    suit the needs of the user, e.g. to run it in legacy optimos mode.
    """

    max_non_improving_actions = 1000
    """The maximum number of actions before the application stops."""
    max_iterations = 1000
    """The maximum (total) number of iterations before the application stops."""

    optimos_legacy_mode = False
    """Should this application behave like an approximation of the original OPTIMOS?"""

    only_allow_low_last = True
    """Should `low` rated Actions be tried last?
 
    E.g. ONLY if no other/higher Action is available.
    """
    optimize_calendar_first = True
    """This is a setting similar to optimos CA/AR | AR/CA Setting

    Should the Calendar be modified first, and then resources added/removed
    or vice versa?

    Also take a look at `legacy_combined_mode_status`, because this setting overrides
    the `optimize_calendar_first` setting.
    """

    print_chosen_actions = False
    """Should the chosen actions be printed?

    This is useful for debugging, but can be very verbose."""

    show_simulation_errors = False
    """Should the simulation errors be shown?

    Most of the time this is not needed, as the errors might just indicate an invalid
    state, which will just result in the action not being chosen.
    """

    legacy_combined_mode_status = LegacyCombinedModeStatus.DISABLED
    """
    This Setting is used to simulate the combined mode of the legacy OPTIMOS.

    The combined mode is a mode where the calendar and resources are optimized at the same time.
    Legacy Optimos will first try calendar and then resources, if the calendar optimization
    finds a result, the resources are still optimized.

    To reproduce this in the new Optimos, we have to do the following:
    - We initialize the setting with calendar first,
    - In this case calendar optimizations will get a higher prio, 
      the resource optimizations will get a "low" prio, that will only(!)
      be executed after the calendar optimization
    - Then as soon as one of the calendar optimzations is successful, 
      we switch this setting to resources first, so that the resources
      are optimized first, and the calendar is optimized afterwards.
    """

    def set_next_combined_mode_status(self) -> None:
        """Set the next combined mode status."""
        self.legacy_combined_mode_status = self.legacy_combined_mode_status.next()
