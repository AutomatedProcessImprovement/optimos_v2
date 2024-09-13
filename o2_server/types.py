from typing import TYPE_CHECKING

from typing_extensions import TypedDict

from o2.models.constraints import ConstraintsType
from o2.models.timetable import TimetableType


class ConfigType(TypedDict):
    """Configuration parameters for the optimization task."""

    scenario_name: str
    num_instances: int
    algorithm: str
    approach: str


class ProcessingRequest(TypedDict):
    """A request to process an optimization task."""

    config: ConfigType
    bpmn_model: str
    timetable: TimetableType
    constraints: ConstraintsType
