import hashlib
from dataclasses import Field, asdict, dataclass, field, replace
from enum import Enum
from functools import reduce
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

from o2.util.bit_mask_helper import any_has_overlap, get_ranges_from_bitmask

if TYPE_CHECKING:
    from o2.models.rule_selector import RuleSelector
    from o2.store import Store
import operator

from o2.models.constraints import BATCH_TYPE, RULE_TYPE, SizeRuleConstraints
from o2.models.days import DAY, DAYS, day_range, is_day_in_range


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

    ALL_DAY_BITMASK = 0b111111111111111111111111

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
    def begin_time_second(self) -> int:
        """Get the start time second."""
        spited = self.begin_time.split(":")
        if len(spited) == 3:
            return int(spited[2])
        return 0

    @property
    def end_time_second(self) -> int:
        """Get the end time second."""
        spited = self.end_time.split(":")
        if len(spited) == 3:
            return int(spited[2])
        return 0

    @property
    def end_time_minute(self) -> int:
        """Get the end time minute."""
        return int(self.end_time.split(":")[1])

    def add_hours_before(self, hours: int) -> Optional["TimePeriod"]:
        """Get new TimePeriod with hours added before."""
        return self._modify(add_start=hours)

    def add_hours_after(self, hours: int) -> Optional["TimePeriod"]:
        """Get new TimePeriod with hours added after."""
        return self._modify(add_end=hours)

    def shift_hours(self, hours: int) -> Optional["TimePeriod"]:
        """Get new TimePeriod with hours shifted.

        If hours is positive, the period is shifted forward.
        """
        return self._modify(add_start=-hours, add_end=hours)

    def _modify(self, add_start: int = 0, add_end: int = 0):
        new_begin = self.begin_time_hour - add_start
        new_end = self.end_time_hour + add_end
        if new_begin < 0 or new_begin >= 24 or new_end < 0 or new_end >= 24:
            return None

        return replace(
            self,
            begin_time=f"{new_begin:02}:{self.begin_time_minute:02}:{self.begin_time_second:02}",
            end_time=f"{new_end:02}:{self.end_time_minute:02}:{self.end_time_second:02}",
        )

    def split_by_day(self) -> List["TimePeriod"]:
        """Split the time period by day.

        Return a list of time periods, one for each day in the range.
        """
        return [
            replace(self, from_=day, to=day) for day in day_range(self.from_, self.to)
        ]

    def to_bitmask(self) -> int:
        """Get a bitmask for the time period.

        Each bit represents an hour in the day.
        The left most bit represents the first hour of the day.
        The right most bit represents the last hour of the day.
        Of course this only includes one day.
        """
        bitarray = [0] * 24
        end = self.end_time_hour
        if self.end_time_minute > 0 or self.end_time_second > 0:
            end += 1
        for i in range(self.begin_time_hour, end):
            bitarray[i] = 1
        return int("".join(map(str, bitarray)), 2)

    def __str__(self) -> str:
        return (
            f"TimePeriod({self.from_},{self.begin_time} -> {self.to},{self.end_time})"
        )

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

    @staticmethod
    def from_start_end(start: int, end: int, day: DAY = DAY.MONDAY) -> "TimePeriod":
        return TimePeriod(
            from_=day,
            to=day,
            begin_time=f"{start:02}:00:00",
            end_time=f"{end:02}:00:00",
        )


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
            if any_has_overlap(bitmasks):
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

    def get_periods_for_day(self, day: DAY) -> List[TimePeriod]:
        """Get the time periods for a specific day."""
        return [tp for tp in self.split_time_periods_by_day() if tp.from_ == day]

    @property
    def total_hours(self) -> int:
        """Get the total number of hours in the calendar."""
        return sum((tp.end_time_hour - tp.begin_time_hour) for tp in self.time_periods)

    @property
    def max_consecutive_hours(self) -> int:
        """Get the maximum number of continuous hours in the calendar."""
        return max((tp.end_time_hour - tp.begin_time_hour) for tp in self.time_periods)

    @property
    def max_periods_per_day(self) -> int:
        """Get the maximum number of periods in a day."""
        return max(len(list(tp.split_by_day())) for tp in self.time_periods)

    @property
    def max_hours_per_day(self) -> int:
        """Get the maximum number of hours in a day."""
        return max(
            sum(tp.end_time_hour - tp.begin_time_hour for tp in time_periods)
            for _, time_periods in self.split_group_by_day()
        )

    @property
    def total_periods(self) -> int:
        """Get the total number of shifts in the calendar."""
        return len(self.split_time_periods_by_day())

    def replace_time_period(
        self, time_period_index: int, time_period: TimePeriod
    ) -> "ResourceCalendar":
        """Replace a time period. Returns a new ResourceCalendar."""
        old_time_period = self.time_periods[time_period_index]
        if (
            old_time_period.from_ != time_period.from_
            or old_time_period.to != time_period.to
        ):
            # If the days are different, we need to split the time
            # periods by day, and only replace the time period
            # for the correct day.
            new_time_periods = time_period.split_by_day()
            old_time_periods = old_time_period.split_by_day()

            combined_time_periods = new_time_periods + [
                tp
                for tp in old_time_periods
                if not is_day_in_range(tp.from_, time_period.from_, time_period.to)
            ]

            return replace(self, time_periods=combined_time_periods)
        else:
            return replace(
                self,
                time_periods=self.time_periods[:time_period_index]
                + [time_period]
                + self.time_periods[time_period_index + 1 :],
            )

    def __str__(self) -> str:
        """Get a string representation of the calendar."""
        return (
            f"ResourceCalendar(id={self.id},\n"
            + ",\t\n".join(map(str, self.time_periods))
            + "\t\n)"
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
    batch_processing: List[BatchingRule] = field(default_factory=list)
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

    def get_resource(self, resource_name: str) -> Optional[Resource]:
        """Get resource (from resource_profiles) with the given name.

        Looks through all resource profiles and returns the first resource,
        that matches the given id.
        """
        for resource_profile in self.resource_profiles:
            for resource in resource_profile.resource_list:
                if resource.name == resource_name:
                    return resource
        return None

    def get_resource_calendar_id(self, resource_id: str) -> Optional[str]:
        """Get the resource calendar id for a resource."""
        resource = self.get_resource(resource_id)
        if resource is None:
            return None
        return resource.calendar

    def get_calendar_for_resource(
        self, resource_name: str
    ) -> Optional[ResourceCalendar]:
        """Get a resource calendar by resource name."""
        calendar_id = self.get_resource_calendar_id(resource_name)
        if calendar_id is None:
            return None
        return self.get_calendar(calendar_id)

    def get_calendar(self, calendar_id: str) -> Optional[ResourceCalendar]:
        """Get a resource calendar by calendar id."""
        for resource_calendar in self.resource_calendars:
            if resource_calendar.id == calendar_id:
                return resource_calendar
        return None

    def replace_resource_calendar(
        self, new_calendar: ResourceCalendar
    ) -> "TimetableType":
        """Replace a resource calendar. Returns a new TimetableType."""
        resource_calendars = [
            new_calendar if rc.id == new_calendar.id else rc
            for rc in self.resource_calendars
        ]
        return replace(self, resource_calendars=resource_calendars)

    @property
    def max_total_hours_per_resource(self) -> int:
        """Get the maximum total hours per resource."""
        return max(
            resource_calendar.total_hours
            for resource_calendar in self.resource_calendars
        )

    @property
    def max_consecutive_hours_per_resource(self) -> int:
        """Get the maximum shift size per resource."""
        return max(
            resource_calendar.max_consecutive_hours
            for resource_calendar in self.resource_calendars
        )

    @property
    def max_periods_per_day_per_resource(self) -> int:
        """Get the maximum shifts per day per resource."""
        return max(
            resource_calendar.max_periods_per_day
            for resource_calendar in self.resource_calendars
        )
