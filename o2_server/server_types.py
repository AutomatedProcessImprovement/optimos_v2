from typing import Callable, Literal, Optional

from typing_extensions import TypedDict

from o2.models.constraints import ConstraintsType
from o2.models.legacy_approach import LegacyApproachAbbreviation
from o2.models.settings import ActionVariationSelection, AgentType, CostType
from o2.models.timetable import TimetableType


class ConfigType(TypedDict):
    """Configuration parameters for the optimization task."""

    scenario_name: str
    num_cases: int
    max_non_improving_actions: int
    max_iterations: int
    max_solutions: Optional[int]
    iterations_per_solution: Optional[int]
    max_actions_per_iteration: Optional[int]
    max_number_of_variations_per_action: Optional[int]
    action_variation_selection: ActionVariationSelection
    sa_temperature: Optional[float]
    sa_cooling_rate: Optional[float]
    sa_solution_order: Optional[Literal["random", "greedy"]]
    approach: Optional[LegacyApproachAbbreviation]
    agent: AgentType
    mode: Literal["batching", "calendar"]
    cost_type: CostType


class ProcessingRequest(TypedDict):
    """A request to process an optimization task."""

    config: ConfigType
    bpmn_model: str
    timetable: TimetableType
    constraints: ConstraintsType
