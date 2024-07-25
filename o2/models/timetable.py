from functools import reduce
import hashlib
from dataclasses import asdict, dataclass, replace
from enum import Enum
from itertools import groupby
from json import dumps
from typing import (
    TYPE_CHECKING,
    Any,
    Generic,
    Iterator,
    List,
    Optional,
    Tuple,
    TypeGuard,
    TypeVar,
    Union,
)

from dataclass_wizard import JSONWizard
from optimos_v2.o2.util.bit_mask_helper import get_ranges_from_bitmask

if TYPE_CHECKING:
    from o2.models.rule_selector import RuleSelector
    from o2.store import Store
import operator

from o2.models.constraints import BATCH_TYPE, RULE_TYPE, SizeRuleConstraints
from o2.models.days import DAY, DAYS, day_range


class COMPARATOR(str, Enum):
    """Different types of comparators."""

    LESS_THEN = "<"
    LESS_THEN_OR_EQUAL = "<="
    GREATER_THEN = ">"
    GREATER_THEN_OR_EQUAL = ">="
    EQUAL = "="


class DISTRIBUTION_TYPE(str, Enum):
    """Different types of probability distributions."""

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
    """A Time Period in a resource calendar."""

    from_: DAY
    """The start of the time period (day, uppercase, e.g. MONDAY)"""

    to: DAY
    """The end of the time period (day, uppercase, e.g. FRIDAY)"""

    begin_time: str
    """The start time of the time period (24h format, e.g. 08:00)"""
    end_time: str  # noqa: N815
    """The end time of the time period (24h format, e.g. 17:00)"""

    class _(JSONWizard.Meta):
        json_key_to_field: Any = {
            "from": "from_",
            "to": "to",
            "beginTime": "begin_time",
            "endTime": "end_time",
            "__all__": True,
        }

    @property
    def begin_time_hour(self) -> int:
        """Get the start time hour."""
        return int(self.begin_time.split(":")[0])

    @property
    def end_time_hour(self) -> int:
        """Get the end time hour."""
        return int(self.end_time.split(":")[0])

    @property
    def begin_time_minute(self) -> int:
        """Get the start time minute."""
        return int(self.begin_time.split(":")[1])

    @property
    def end_time_minute(self) -> int:
        """Get the end time minute."""
        return int(self.end_time.split(":")[1])

    def add_hours_before(self, hours: int) -> "TimePeriod":
        """Get new TimePeriod with hours added before."""
        return self._modify(add_start=hours)

    def add_hours_after(self, hours: int) -> "TimePeriod":
        """Get new TimePeriod with hours added after."""
        return self._modify(add_end=hours)

    def shift_hours(self, hours: int) -> "TimePeriod":
        """Get new TimePeriod with hours shifted.

        If hours is positive, the period is shifted forward.
        """
        return self._modify(add_start=-hours, add_end=hours)

    def _modify(self, add_start: int = 0, add_end: int = 0):
        new_begin = self.begin_time_hour + add_start
        new_end = self.end_time_hour + add_end
        if new_begin < 0 or new_begin >= 24 or new_end < 0 or new_end >= 24:
            raise ValueError("Out of bounds")

        return replace(
            self,
            begin_time=f"{new_begin:02}:{self.begin_time_minute}",
            end_time=f"{new_end:02}:{self.end_time_minute}",
        )

    def split_by_day(self) -> List["TimePeriod"]:
        """Split the time period by day.

        Return a list of time periods, one for each day in the range.
        """
        return [
            replace(self, from_=day, to=day) for day in day_range(self.from_, self.to)
        ]

    def to_bitmask(self) -> int:
        """Get a bitmask for the time period."""
        return sum(1 << i for i in range(self.begin_time_hour, self.end_time_hour))

    @staticmethod
    def from_bitmask(bitmask: int, day: DAY) -> List["TimePeriod"]:
        """Create a time period from a bitmask."""
        hour_ranges = get_ranges_from_bitmask(bitmask)
        return [
            TimePeriod(
                from_=day,
                to=day,
                begin_time=f"{start:02}:00",
                end_time=f"{end:02}:00",
            )
            for start, end in hour_ranges
        ]


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

    def is_valid(self) -> bool:
        """Check if the calendar is valid.

        The calendar is valid if all time periods have a begin time before the end time.
        And if the time periods are not overlapping.
        """
        grouped_time_periods = self.split_group_by_day()
        for _, time_periods_iter in grouped_time_periods:
            time_periods = list(time_periods_iter)
            for tp in time_periods:
                if tp.begin_time >= tp.end_time:
                    return False

            bitmasks = [tp.to_bitmask() for tp in time_periods]
            if reduce(operator.or_, bitmasks, False):
                return False
        return True

    def split_group_by_day(self) -> Iterator[tuple[DAY, Iterator[TimePeriod]]]:
        """Split the time periods by day."""
        return groupby(self.split_time_periods_by_day(), key=lambda tp: tp.from_)

    def split_time_periods_by_day(self) -> List[TimePeriod]:
        """Split the time periods by day and sort them."""
        return sorted(
            (tp for tp in self.time_periods for tp in tp.split_by_day()),
            key=lambda tp: tp.from_,
        )


@dataclass(frozen=True)
class EventDistribution(JSONWizard):
    pass


@dataclass(frozen=True)
class Distribution(JSONWizard):
    key: Union[str, int]
    value: float


V = TypeVar("V", DAY, int)


@dataclass(frozen=True, eq=True)
class FiringRule(JSONWizard, Generic[V]):
    """A rule for when to fire (activate) a batching rule."""

    attribute: RULE_TYPE
    comparison: COMPARATOR
    value: V

    def __eq__(self, other: object) -> bool:
        """Check if two rules are equal."""
        return (
            isinstance(other, FiringRule)
            and self.attribute == other.attribute
            and self.comparison == other.comparison
            and self.value == other.value
        )

    def id(self) -> str:
        """Get a thread-safe id for the rule.

        We need to use this and not hash, because hash will not give you the same result on different threads.
        """
        # TODO Use a more performant hash function
        return hashlib.md5(str(dumps(asdict(self))).encode()).hexdigest()


AndRules = List[FiringRule]
OrRules = List[AndRules]


def rule_is_large_wt(rule: Optional[FiringRule]) -> TypeGuard[FiringRule[int]]:
    """Check if a rule is a large waiting time rule."""
    return rule is not None and rule.attribute == RULE_TYPE.LARGE_WT


def rule_is_week_day(rule: Optional[FiringRule]) -> TypeGuard[FiringRule[DAY]]:
    """Check if a rule is a week day rule."""
    return rule is not None and rule.attribute == RULE_TYPE.WEEK_DAY


def rule_is_size(rule: Optional[FiringRule]) -> TypeGuard[FiringRule[int]]:
    """Check if a rule is a size rule."""
    return rule is not None and rule.attribute == RULE_TYPE.SIZE


def rule_is_ready_wt(rule: Optional[FiringRule]) -> TypeGuard[FiringRule[int]]:
    """Check if a rule is a ready waiting time rule."""
    return rule is not None and rule.attribute == RULE_TYPE.READY_WT


def rule_is_daily_hour(rule: Optional[FiringRule]) -> TypeGuard[FiringRule[int]]:
    """Check if a rule is a daily hour rule."""
    return rule is not None and rule.attribute == RULE_TYPE.DAILY_HOUR


@dataclass(frozen=True)
class BatchingRule(JSONWizard):
    task_id: str
    type: BATCH_TYPE
    size_distrib: list[Distribution]
    duration_distrib: list[Distribution]
    firing_rules: OrRules

    def can_be_modified(self, store: "Store", size_increment: int) -> bool:
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

    def get_firing_rule(self, rule_selector: "RuleSelector") -> Optional[FiringRule]:
        """Get a firing rule by rule selector."""
        if rule_selector.firing_rule_index is None:
            return None
        or_index = rule_selector.firing_rule_index[0]
        and_index = rule_selector.firing_rule_index[1]
        return self.firing_rules[or_index][and_index]

    def remove_firing_rule(
        self, rule_selector: "RuleSelector"
    ) -> "Optional[BatchingRule]":
        """Remove a firing rule. Returns a new BatchingRule."""
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
                + [and_rules]
                + self.firing_rules[or_index + 1 :]
            )

        if len(or_rules) == 0:
            return None
        return replace(self, firing_rules=or_rules)

    def replace_firing_rule(
        self, rule_selector: "RuleSelector", new_rule: FiringRule
    ) -> "BatchingRule":
        """Replace a firing rule. Returns a new BatchingRule."""
        assert rule_selector.firing_rule_index is not None
        or_index = rule_selector.firing_rule_index[0]
        and_index = rule_selector.firing_rule_index[1]
        and_rules = (
            self.firing_rules[or_index][:and_index]
            + [new_rule]
            + self.firing_rules[or_index][and_index + 1 :]
        )

        or_rules = (
            self.firing_rules[:or_index]
            + [and_rules]
            + self.firing_rules[or_index + 1 :]
        )

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

    def get_batching_rule(
        self, rule_selector: "RuleSelector"
    ) -> Union[Tuple[int, BatchingRule], Tuple[None, None]]:
        """Get a batching rule by rule selector."""
        return next(
            (
                (i, rule)
                for i, rule in enumerate(self.batch_processing)
                if rule.task_id == rule_selector.batching_rule_task_id
            ),
            (
                None,
                None,
            ),
        )
