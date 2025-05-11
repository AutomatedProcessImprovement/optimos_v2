"""GranuleSize class for defining time granularity."""

from dataclasses import dataclass
from typing import Literal

from dataclass_wizard import JSONWizard


@dataclass(frozen=True)
class GranuleSize(JSONWizard):
    """Defines the granularity of time measurements."""

    value: int = 60
    time_unit: Literal["MINUTES"] = "MINUTES"

    class _(JSONWizard.Meta):
        skip_defaults = False
