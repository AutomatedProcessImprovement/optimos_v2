from dataclasses import dataclass
from typing import List, Union

from typing_extensions import TypedDict
from dataclass_wizard import JSONWizard


@dataclass(frozen=True)
class ResourceListItem(JSONWizard):
    id: str
    name: str
    cost_per_hour: int
    amount: int
    calendar: str
    assigned_tasks: List[str]


@dataclass(frozen=True)
class ResourceProfilesItem(JSONWizard):
    id: str
    name: str
    resource_list: List[ResourceListItem]


@dataclass(frozen=True)
class DistributionParamsItem(JSONWizard):
    value: Union[float, int]


@dataclass(frozen=True)
class ArrivalTimeDistribution(JSONWizard):
    distribution_name: str
    distribution_params: List[DistributionParamsItem]


TimePeriodsItem = TypedDict(
    "TimePeriodsItem",
    {
        "from": str,
        "to": str,
        "beginTime": str,
        "endTime": str,
    },
)


@dataclass(frozen=True)
class ProbabilitiesItem0(JSONWizard):
    path_id: str
    value: float


@dataclass(frozen=True)
class GatewayBranchingProbabilitiesItem(JSONWizard):
    gateway_id: str
    probabilities: List[ProbabilitiesItem0]


@dataclass(frozen=True)
class TimetableResourceItem(JSONWizard):
    resource_id: str
    distribution_name: str
    distribution_params: List[DistributionParamsItem]


@dataclass(frozen=True)
class TaskResourceDistributionItem(JSONWizard):
    task_id: str
    resources: List[TimetableResourceItem]


@dataclass(frozen=True)
class ResourceCalendarsItem(JSONWizard):
    id: str
    name: str
    time_periods: List[TimePeriodsItem]


@dataclass(frozen=True)
class EventDistribution(JSONWizard):
    pass


@dataclass(frozen=True)
class Distribution(JSONWizard):
    key: str
    value: float


@dataclass(frozen=True)
class FiringRule(JSONWizard):
    attribute: str
    comparison: str
    value: int


@dataclass(frozen=True)
class BatchingRule(JSONWizard):
    task_id: str
    type: str
    size_distrib: List[Distribution]
    duration_distrib: List[Distribution]
    firing_rules: List[List[FiringRule]]


@dataclass(frozen=True)
class TimetableType(JSONWizard):
    resource_profiles: List[ResourceProfilesItem]
    arrival_time_distribution: ArrivalTimeDistribution
    arrival_time_calendar: List[TimePeriodsItem]
    gateway_branching_probabilities: List[GatewayBranchingProbabilitiesItem]
    task_resource_distribution: List[TaskResourceDistributionItem]
    resource_calendars: List[ResourceCalendarsItem]
    event_distribution: EventDistribution
    batch_processing: List[BatchingRule]

    class _(JSONWizard.Meta):
        key_transform_with_dump = "SNAKE"
