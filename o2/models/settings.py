from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from o2.actions.modify_calendar_base_action import ModifyCalendarBaseAction
from o2.actions.modify_resource_base_action import ModifyResourceBaseAction

if TYPE_CHECKING:
    from o2.actions.base_action import BaseAction


class LegacyApproach(str, Enum):
    """The status of the legacy combined mode.

    See Settings.legacy_combined_mode_status for more information.
    """

    COMBINED_CALENDAR_NEXT = "COMBINED_CALENDAR_NEXT"
    COMBINED_RESOURCES_NEXT = "COMBINED_RESOURCES_NEXT"

    CALENDAR_ONLY = "CALENDAR_ONLY"
    RESOURCES_ONLY = "RESOURCES_ONLY"

    CALENDAR_FIRST = "CALENDAR_FIRST"
    RESOURCES_FIRST = "RESOURCES_FIRST"

    def next(self) -> "LegacyApproach":
        """Get the next status in the cycle."""
        if self == LegacyApproach.COMBINED_CALENDAR_NEXT:
            return LegacyApproach.COMBINED_RESOURCES_NEXT
        if self == LegacyApproach.COMBINED_RESOURCES_NEXT:
            return LegacyApproach.COMBINED_CALENDAR_NEXT
        return self

    @property
    def combined_enabled(self) -> bool:
        """Return whether the combined mode is enabled."""
        return (
            self == LegacyApproach.COMBINED_CALENDAR_NEXT
            or self == LegacyApproach.COMBINED_RESOURCES_NEXT
        )

    @property
    def calendar_is_next(self) -> bool:
        """Return whether the calendar is next in the combined mode."""
        return (
            self == LegacyApproach.COMBINED_CALENDAR_NEXT
            or self == LegacyApproach.CALENDAR_FIRST
            or self == LegacyApproach.CALENDAR_ONLY
        )

    @property
    def calendar_is_disabled(self) -> bool:
        """Return whether the calendar is disabled in the combined mode."""
        return self == LegacyApproach.RESOURCES_ONLY

    @property
    def resource_is_next(self) -> bool:
        """Return whether the resources are next in the combined mode."""
        return (
            self == LegacyApproach.COMBINED_RESOURCES_NEXT
            or self == LegacyApproach.RESOURCES_FIRST
            or self == LegacyApproach.RESOURCES_ONLY
        )

    @property
    def resource_is_disabled(self) -> bool:
        """Return whether the resources are disabled in the combined mode."""
        return self == LegacyApproach.CALENDAR_ONLY

    def action_matches(self, action: "BaseAction") -> bool:
        """Return whether the action matches the current combined mode status."""
        if self == LegacyApproach.COMBINED_CALENDAR_NEXT:
            return isinstance(action, ModifyCalendarBaseAction)
        if self == LegacyApproach.COMBINED_RESOURCES_NEXT:
            return isinstance(action, ModifyResourceBaseAction)
        return False

    @staticmethod
    def from_abbreviation(abbreviation: str) -> "LegacyApproach":
        """Get the LegacyApproach from its abbreviation."""
        if abbreviation == "CAAR":
            return LegacyApproach.CALENDAR_FIRST
        if abbreviation == "ARCA":
            return LegacyApproach.RESOURCES_FIRST
        if abbreviation == "CO":
            return LegacyApproach.COMBINED_CALENDAR_NEXT
        if abbreviation == "CA":
            return LegacyApproach.CALENDAR_ONLY
        if abbreviation == "AR":
            return LegacyApproach.RESOURCES_ONLY
        raise ValueError(f"Unknown abbreviation: {abbreviation}")


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

    print_chosen_actions = False
    """Should the chosen actions be printed?

    This is useful for debugging, but can be very verbose."""

    show_simulation_errors = False
    """Should the simulation errors be shown?

    Most of the time this is not needed, as the errors might just indicate an invalid
    state, which will just result in the action not being chosen.
    """

    legacy_approach = LegacyApproach.CALENDAR_FIRST
    """
    This Setting is used to simulate different approaches used by legacy optimos.

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
        self.legacy_approach = self.legacy_approach.next()
