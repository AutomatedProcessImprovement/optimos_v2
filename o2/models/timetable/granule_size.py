from dataclasses import dataclass
from typing import Literal

from dataclass_wizard import JSONWizard


@dataclass(frozen=True)
class GranuleSize(JSONWizard):
    """Defines the granularity of time measurements."""

    value: int = 60
    time_unit: Literal["MINUTES"] = "MINUTES"

    class _(JSONWizard.Meta):  # noqa: N801
        skip_defaults = False
