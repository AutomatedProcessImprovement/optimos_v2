from dataclasses import dataclass
from typing import Union

from dataclass_wizard import JSONWizard


@dataclass(frozen=True)
class DistributionParameter(JSONWizard):
    """A parameter for a distribution."""

    value: Union[float, int]
