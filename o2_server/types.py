from enum import Enum
from typing import Optional

from typing_extensions import TypedDict

from o2.models.constraints import ConstraintsType
from o2.models.settings import AgentType
from o2.models.timetable import TimetableType


class ConfigType(TypedDict):
    """Configuration parameters for the optimization task."""

    scenario_name: str
    num_cases: int
    max_non_improving_actions: int
    max_iterations: int
    max_actions_per_iteration: Optional[int]
    approach: str
    agent: AgentType
    disable_batch_optimization: bool


class ProcessingRequest(TypedDict):
    """A request to process an optimization task."""

    config: ConfigType
    bpmn_model: str
    timetable: TimetableType
    constraints: ConstraintsType
