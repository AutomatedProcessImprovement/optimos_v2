from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from o2.actions.base_actions.base_action import BaseAction


class LegacyApproach(str, Enum):
    """The status of the legacy combined mode.

    See Settings.legacy_combined_mode_status for more information.
    """

    COMBINED = "COMBINED"

    CALENDAR_ONLY = "CALENDAR_ONLY"
    RESOURCES_ONLY = "RESOURCES_ONLY"

    CALENDAR_FIRST = "CALENDAR_FIRST"
    RESOURCES_FIRST = "RESOURCES_FIRST"

    @property
    def calendar_is_disabled(self) -> bool:
        """Return whether the calendar is disabled in the combined mode."""
        return self == LegacyApproach.RESOURCES_ONLY

    @property
    def resource_is_disabled(self) -> bool:
        """Return whether the resources are disabled in the combined mode."""
        return self == LegacyApproach.CALENDAR_ONLY

    @staticmethod
    def from_abbreviation(abbreviation: str) -> "LegacyApproach":
        """Get the LegacyApproach from its abbreviation."""
        if abbreviation == "CAAR":
            return LegacyApproach.CALENDAR_FIRST
        if abbreviation == "ARCA":
            return LegacyApproach.RESOURCES_FIRST
        if abbreviation == "CO":
            return LegacyApproach.COMBINED
        if abbreviation == "CA":
            return LegacyApproach.CALENDAR_ONLY
        if abbreviation == "AR":
            return LegacyApproach.RESOURCES_ONLY
        raise ValueError(f"Unknown abbreviation: {abbreviation}")
