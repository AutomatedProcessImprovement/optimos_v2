from dataclasses import asdict, dataclass, field, replace
from enum import Enum
from json import dumps
from typing import Any, List, Optional, Union

from typing_extensions import TypedDict
from dataclass_wizard import JSONWizard, json_field, json_key
from typing import TYPE_CHECKING
import hashlib


if TYPE_CHECKING:
    from o2.types.rule_selector import RuleSelector
    from o2.store import Store
from o2.types.days import DAY
from o2.types.constraints import BATCH_TYPE, RULE_TYPE, SizeRuleConstraints


class COMPARATOR(str, Enum):
    LESS_THEN = "<"
    LESS_THEN_OR_EQUAL = "<="
    GREATER_THEN = ">"
    GREATER_THEN_OR_EQUAL = ">="
    EQUAL = "="


class DISTRIBUTION_TYPE(str, Enum):
    # No distribution
    FIXED = "fix"

    # Uniform aka random between, min and max
    # (Using numpy.random.uniform)
    UNIFORM = "default"

    # The rest of the distributions are from scipy.stats
    NORMAL = "norm"
    EXPONENTIAL = "expon"
    EXPONENTIAL_NORMAL = "exponnorm"
    GAMMA = "gamma"
    TRIANGULAR = "triang"
    LOG_NORMAL = "lognorm"


@dataclass(frozen=True)
class Resource(JSONWizard):
    id: str
    name: str
    cost_per_hour: int
    amount: int
    calendar: str
    assigned_tasks: List[str]


@dataclass(frozen=True)
class ResourcePool(JSONWizard):
    id: str
    name: str
    resource_list: List[Resource]


@dataclass(frozen=True)
class DistributionParameter(JSONWizard):
    value: Union[float, int]


@dataclass(frozen=True)
class ArrivalTimeDistribution(JSONWizard):
    distribution_name: DISTRIBUTION_TYPE
    distribution_params: List[DistributionParameter]


@dataclass(frozen=True)
class TimePeriod(JSONWizard):
    from_: DAY
    to: DAY
    beginTime: str
    endTime: str

    class _(JSONWizard.Meta):
        json_key_to_field: Any = {
            "from": "from_",
            "to": "to",
            "beginTime": "beginTime",
            "endTime": "endTime",
            "__all__": True,
        }


@dataclass(frozen=True)
class Probability(JSONWizard):
    path_id: str
    value: float


@dataclass(frozen=True)
class GatewayBranchingProbability(JSONWizard):
    gateway_id: str
    probabilities: List[Probability]


@dataclass(frozen=True)
class TaskResourceDistribution(JSONWizard):
    resource_id: str
    distribution_name: str
    distribution_params: List[DistributionParameter]


@dataclass(frozen=True)
class TaskResourceDistributions(JSONWizard):
    task_id: str
    resources: List[TaskResourceDistribution]


@dataclass(frozen=True)
class ResourceCalendar(JSONWizard):
    id: str
    name: str
    time_periods: List[TimePeriod]


@dataclass(frozen=True)
class EventDistribution(JSONWizard):
    pass


@dataclass(frozen=True)
class Distribution(JSONWizard):
    key: Union[str, int]
    value: float


@dataclass(frozen=True, eq=True)
class FiringRule(JSONWizard):
    attribute: RULE_TYPE
    comparison: COMPARATOR
    value: int

    def __eq__(self, other):
        return (
            self.attribute == other.attribute
            and self.comparison == other.comparison
            and self.value == other.value
        )

    def id(self):
        # TODO Use a more performant hash function
        return hashlib.md5(str(dumps(asdict(self))).encode()).hexdigest()


AndRules = List[FiringRule]
OrRules = List[AndRules]


@dataclass(frozen=True)
class BatchingRule(JSONWizard):
    task_id: str
    type: BATCH_TYPE
    size_distrib: list[Distribution]
    duration_distrib: list[Distribution]
    firing_rules: OrRules

    def can_be_modified(self, store: "Store", size_increment: int):
        matching_constraints = store.constraints.get_batching_constraints_for_task(
            self.task_id
        )

        for constraint in matching_constraints:
            if constraint is SizeRuleConstraints:
                if constraint.min_size > int(self.size_distrib[0].key) + size_increment:
                    return False
                if constraint.max_size < int(self.size_distrib[0].key) + size_increment:
                    return False
        return True

    def id(self):
        # TODO Use a more performant hash function
        return hashlib.md5(str(dumps(asdict(self))).encode()).hexdigest()

    def remove_firing_rule(self, rule_selector: "RuleSelector"):
        assert rule_selector.firing_rule_index is not None
        or_index = rule_selector.firing_rule_index[0]
        and_index = rule_selector.firing_rule_index[1]
        and_rules = (
            self.firing_rules[or_index][:and_index]
            + self.firing_rules[or_index][and_index + 1 :]
        )

        if len(and_rules) == 0:
            or_rules = self.firing_rules[:or_index] + self.firing_rules[or_index + 1 :]
        else:
            or_rules = (
                self.firing_rules[:or_index]
                + and_rules
                + self.firing_rules[or_index + 1 :]
            )

        if len(or_rules) == 0:
            return None
        return replace(self, firing_rules=or_rules)


@dataclass(frozen=True)
class TimetableType(JSONWizard):
    resource_profiles: List[ResourcePool]
    arrival_time_distribution: ArrivalTimeDistribution
    arrival_time_calendar: List[TimePeriod]
    gateway_branching_probabilities: List[GatewayBranchingProbability]
    task_resource_distribution: List[TaskResourceDistributions]
    resource_calendars: List[ResourceCalendar]
    event_distribution: EventDistribution
    batch_processing: List[BatchingRule]
    start_time: str = "2000-01-01T00:00:00Z"
    total_cases: int = 1000

    class _(JSONWizard.Meta):
        key_transform_with_dump = "SNAKE"
