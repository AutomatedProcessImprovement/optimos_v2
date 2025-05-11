"""Base class for all batching constraints."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING

from dataclass_wizard import JSONWizard

from o2.models.timetable import BATCH_TYPE, RULE_TYPE

if TYPE_CHECKING:
    from o2.models.timetable import TimetableType


@dataclass(frozen=True)
class BatchingConstraints(JSONWizard, ABC):
    """Base class for all batching constraints."""

    id: str
    tasks: list[str]
    batch_type: BATCH_TYPE
    rule_type: RULE_TYPE

    @abstractmethod
    def verify_timetable(self, timetable: "TimetableType") -> bool:
        """Check if the timetable is valid against the constraints."""
        pass
