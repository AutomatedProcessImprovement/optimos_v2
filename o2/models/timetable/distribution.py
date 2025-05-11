"""Distribution class for mapping keys to value distributions."""

from dataclasses import dataclass
from typing import Union

from dataclass_wizard import JSONWizard


@dataclass(frozen=True)
class Distribution(JSONWizard):
    """Maps a key to a distribution value."""

    key: Union[str, int]
    value: float
