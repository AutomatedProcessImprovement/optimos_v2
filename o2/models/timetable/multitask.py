from dataclasses import dataclass
from typing import Optional

from dataclass_wizard import JSONWizard

from o2.models.days import DAY


@dataclass(frozen=True)
class ParallelTaskProbability(JSONWizard):
    """The probability of a resource to be used for a certain number of parallel tasks."""

    parallel_tasks: int
    probability: float


@dataclass(frozen=True)
class TimePeriodWithParallelTaskProbability(JSONWizard):
    """A time period with information about the probability of parallel tasks."""

    from_: "DAY"
    """The start of the time period (day, uppercase, e.g. MONDAY)

    NOTE: In the json the field is called `from` (from is a reserved keyword in Python)
    """

    to: "DAY"
    """The end of the time period (day, uppercase, e.g. FRIDAY)"""

    begin_time: str
    """The start time of the time period (24h format, e.g. 08:00)"""
    end_time: str
    """The end time of the time period (24h format, e.g. 17:00)"""
    multitask_info: Optional[list[ParallelTaskProbability]] = None

    class _(JSONWizard.Meta):
        json_key_to_field = {
            "__all__": True,  # type: ignore
            "from": "from_",
            "beginTime": "begin_time",
            "endTime": "end_time",
        }


@dataclass(frozen=True)
class MultitaskResourceInfo(JSONWizard):
    """The information about a resource that can handle multiple tasks in parallel."""

    resource_id: str
    r_workload: float
    multitask_info: Optional[list[ParallelTaskProbability]] = None
    weekly_probability: Optional[list[list[TimePeriodWithParallelTaskProbability]]] = None


@dataclass(frozen=True)
class Multitask(JSONWizard):
    """The information about all resources that can handle multiple tasks in parallel."""

    type: str
    values: list[MultitaskResourceInfo]
