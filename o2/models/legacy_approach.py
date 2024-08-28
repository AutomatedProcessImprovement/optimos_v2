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

    def next_combined(self) -> "LegacyApproach":
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
