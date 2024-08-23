import hashlib
import re
from dataclasses import asdict, dataclass, field, replace
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

from o2.models.legacy_constraints import WorkMasks
from o2.util.bit_mask_helper import any_has_overlap, get_ranges_from_bitmask
from o2.util.helper import CLONE_REGEX, name_is_clone_of, random_string

if TYPE_CHECKING:
    from o2.models.rule_selector import RuleSelector
    from o2.store import Store
import operator

from o2.models.constraints import BATCH_TYPE, RULE_TYPE, SizeRuleConstraints
from o2.models.days import DAY, day_range, is_day_in_range


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

    def get_total_cost(self, timetable: "TimetableType") -> int:
        """Get the total cost of the resource."""
        calendar = timetable.get_calendar(self.calendar)
        if calendar is None:
            return 0
        return self.cost_per_hour * calendar.total_hours

    def can_safely_be_removed(self, timetable: "TimetableType") -> bool:
        """Check if the resource can be removed safely.

        A resource can be removed safely if it's assigned tasks all have
        other resources that can do the task.
        """
        for task_id in self.assigned_tasks:
            profile = timetable.get_resource_profile(task_id)
            if profile is None:
                continue
            if len(profile.resource_list) <= 1:
                return False
        return True

    def clone(self, assigned_tasks: List[str]) -> "Resource":
        """Clone the resource with new assigned tasks."""
        base_name = self.name
        match = CLONE_REGEX.match(self.name)
        if match is not None:
            base_name = match.group(1)

        new_name_id = f"{base_name}_clone_{random_string(8)}"
        return replace(
            self,
            id=new_name_id,
            name=new_name_id,
            calendar=f"{new_name_id}timetable",
            assigned_tasks=assigned_tasks,
        )

    def remove_task(self, task_id: str) -> "Resource":
        """Remove a task from the resource."""
        return replace(
            self,
            assigned_tasks=[task for task in self.assigned_tasks if task != task_id],
        )

    def is_clone_of(self, resource: "Resource") -> bool:
        """Check if the resource is a clone of another resource."""
        match = CLONE_REGEX.match(self.name)
        return match is not None and match.group(1) == resource.name


@dataclass(frozen=True)
class ResourcePool(JSONWizard):
    id: str
    name: str
    resource_list: List[Resource]

    def remove_resource(self, resource_id: str) -> "ResourcePool":
        """Remove a resource from the pool."""
        return replace(
            self,
            resource_list=[
                resource
                for resource in self.resource_list
                if resource.id != resource_id
            ],
        )

    def update_resource(self, updated_resource: Resource) -> "ResourcePool":
        """Update a resource in the pool."""
        return replace(
            self,
            resource_list=[
                updated_resource if updated_resource.id == resource.id else resource
                for resource in self.resource_list
            ],
        )


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

    @property
    def duration(self) -> int:
        """Get the duration of the time period in hours."""
        return self.end_time_hour - self.begin_time_hour

    @property
    def is_empty(self) -> bool:
        """Check if the time period is empty."""
        return self.begin_time == self.end_time

    def add_hours_before(self, hours: int) -> Optional["TimePeriod"]:
        """Get new TimePeriod with hours added before."""
        return self._modify(add_start=hours)

    def add_hours_after(self, hours: int) -> Optional["TimePeriod"]:
        """Get new TimePeriod with hours added after."""
        return self._modify(add_end=hours)

    def shift_hours(self, hours: int) -> Optional["TimePeriod"]:
        """Get new TimePeriod with hours shifted.

        If hours is positive, the period is shifted forward.
        (Begins later and ends later)
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
        if self.is_empty:
            return []
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

    @staticmethod
    def empty(day: DAY = DAY.MONDAY) -> "TimePeriod":
        return TimePeriod(
            from_=day,
            to=day,
            begin_time="00:00:00",
            end_time="00:00:00",
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

    def remove_resource(self, resource_id: str) -> "TaskResourceDistributions":
        """Remove a resource from the distribution."""
        return replace(
            self,
            resources=[
                resource
                for resource in self.resources
                if resource.resource_id != resource_id
            ],
        )

    def add_resource(
        self, distribution: TaskResourceDistribution
    ) -> "TaskResourceDistributions":
        """Add a resource to the distribution."""
        return replace(
            self,
            resources=self.resources + [distribution],
        )

    def add_resource_based_on_original(
        self, original_resource_id: str, new_resource_id: str
    ) -> "TaskResourceDistributions":
        """Add a resource based on an original resource.

        If the original resource is not found, the distribution is not changed.
        """
        original_distribution = next(
            (
                resource
                for resource in self.resources
                if resource.resource_id == original_resource_id
            ),
            None,
        )
        if original_distribution is None:
            return self

        new_resource = replace(original_distribution, resource_id=new_resource_id)
        return self.add_resource(new_resource)


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

    def get_periods_containing_day(self, day: DAY) -> List[TimePeriod]:
        """Get the time periods that contain a specific day."""
        return [tp for tp in self.time_periods if is_day_in_range(day, tp.from_, tp.to)]

    def to_work_masks(self) -> WorkMasks:
        """Convert the calendar to work masks."""
        days = {
            f"{day.name.lower()}": reduce(
                operator.or_, [tp.to_bitmask() for tp in time_periods]
            )
            for day, time_periods in self.split_group_by_day()
        }
        return WorkMasks(**days)

    @property
    def total_hours(self) -> int:
        """Get the total number of hours in the calendar."""
        return sum(
            (tp.end_time_hour - tp.begin_time_hour)
            for tp in self.split_time_periods_by_day()
        )

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

        if time_period.is_empty:
            # The old period was only one day long, so we can just remove it
            if old_time_period.from_ == old_time_period.to:
                return replace(
                    self,
                    time_periods=self.time_periods[:time_period_index]
                    + self.time_periods[time_period_index + 1 :],
                )
            else:
                # The old period was multiple days long, so we need to split it
                # and only remove the correct day
                new_time_periods = [
                    tp
                    for tp in old_time_period.split_by_day()
                    if tp.from_ != time_period.from_
                ]
                return replace(
                    self,
                    time_periods=self.time_periods[:time_period_index]
                    + new_time_periods
                    + self.time_periods[time_period_index + 1 :],
                )
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

    def can_remove_firing_rule(self, or_index: int, and_index: int) -> bool:
        """Check if a firing rule can be removed.

        Checks:
        - We cannot remove a size rule from a DAILY_HOUR rule set.
        """
        if self.firing_rules[or_index][and_index].attribute == RULE_TYPE.SIZE:
            return all(
                rule.attribute != RULE_TYPE.DAILY_HOUR
                for rule in self.firing_rules[or_index]
            )
        return True

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
                # For compatibility with legacy Optimos, we also check for the
                # resource name with "timetable" appended.
                if (
                    resource.name == resource_name
                    or resource.id == (resource_name + "timetable")
                    or (resource.id + "timetable") == resource_name
                ):
                    return resource
        return None

    def get_task_resource_distribution(
        self, task_id: str
    ) -> Optional[TaskResourceDistributions]:
        """Get task resource distribution by task id."""
        for task_resource_distribution in self.task_resource_distribution:
            if task_resource_distribution.task_id == task_id:
                return task_resource_distribution
        return None

    def get_resource_profiles_containing_resource(
        self, resource_id: str
    ) -> list[ResourcePool]:
        """Get the resource profiles containing a resource."""
        return [
            resource_profile
            for resource_profile in self.resource_profiles
            if any(
                resource.id == resource_id
                for resource in resource_profile.resource_list
            )
        ]

    def get_resource_profile(self, profile_id: str) -> Optional[ResourcePool]:
        """Get a resource profile by profile id.

        Legacy Optimos considers the profile id to be a task id.
        """
        return next(
            (
                resource_profile
                for resource_profile in self.resource_profiles
                if resource_profile.id == profile_id
            ),
            None,
        )

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

    def get_calendars_for_resource_clones(
        self, resource_name: str
    ) -> List[ResourceCalendar]:
        """Get all resource calendars of clones of a resource."""
        return [
            resource_calendar
            for resource_calendar in self.resource_calendars
            if name_is_clone_of(resource_calendar.name, resource_name)
        ]

    def get_calendar(self, calendar_id: str) -> Optional[ResourceCalendar]:
        """Get a resource calendar by calendar id."""
        for resource_calendar in self.resource_calendars:
            if resource_calendar.id == calendar_id:
                return resource_calendar
        return None

    def get_all_resources(self) -> List[Resource]:
        """Get all resources."""
        resources = {
            resource.id: resource
            for resource_profile in self.resource_profiles
            for resource in resource_profile.resource_list
        }
        return list(resources.values())

    def get_resources_with_cost(self) -> List[tuple[Resource, int]]:
        """Get all resources with cost. Sorted desc."""
        return sorted(
            (
                (
                    resource_profile,
                    resource_profile.get_total_cost(self),
                )
                for resource_profile in self.get_all_resources()
            ),
            key=operator.itemgetter(1),
            reverse=True,
        )

    def replace_resource_calendar(
        self, new_calendar: ResourceCalendar
    ) -> "TimetableType":
        """Replace a resource calendar. Returns a new TimetableType."""
        resource_calendars = [
            new_calendar if rc.id == new_calendar.id else rc
            for rc in self.resource_calendars
        ]
        return replace(self, resource_calendars=resource_calendars)

    def remove_resource(self, resource_id: str) -> "TimetableType":
        """Get a new timetable with a resource removed."""
        resource = self.get_resource(resource_id)
        if resource is None:
            return self

        new_resource_profiles = [
            resource_profile.remove_resource(resource_id)
            for resource_profile in self.resource_profiles
        ]

        new_task_resource_distribution = [
            task_resource_distribution.remove_resource(resource_id)
            for task_resource_distribution in self.task_resource_distribution
        ]

        new_resource_calendars = [
            resource_calendar
            for resource_calendar in self.resource_calendars
            if resource_calendar.id != resource.calendar
        ]

        return replace(
            self,
            resource_profiles=new_resource_profiles,
            task_resource_distribution=new_task_resource_distribution,
            resource_calendars=new_resource_calendars,
        )

    def clone_resource(
        self, resource_id: str, assigned_tasks: list[str]
    ) -> "TimetableType":
        """Get a new timetable with a resource duplicated.

        The new resource will only have the assigned tasks given,
        but copy all other properties from the original resource.

        The Clone will be added in three places:
        1. in the resource calendars
        2. in the resource pools of the assigned_tasks
        3. in the task_resource_distribution of the assigned_tasks

        The Resource Constraints will not be cloned, because the original
        constraints will automatically be "assigned" based on the name.

        The Naming of the resource will also reflect clones of clones,
        meaning a clone of a clone will have the same name to a first level clone
        """
        original_resource = self.get_resource(resource_id)
        if original_resource is None:
            return self
        resource_clone = original_resource.clone(assigned_tasks)

        cloned_resource_calendars = self._clone_resource_calendars(
            original_resource, resource_clone, assigned_tasks
        )

        cloned_resource_profiles = self._clone_resource_profiles(
            original_resource, resource_clone, assigned_tasks
        )

        cloned_resource_distribution = self._clone_task_distributions(
            original_resource, resource_clone, assigned_tasks
        )
        return replace(
            self,
            resource_profiles=cloned_resource_profiles,
            task_resource_distribution=cloned_resource_distribution,
            resource_calendars=cloned_resource_calendars,
        )

    def remove_task_from_resource(
        self, resource_id: str, task_id: str
    ) -> "TimetableType":
        """Get a new timetable with a task removed from a resource.

        The task will be removed from the resource's assigned tasks.
        The resource will be removed from the task's resource distribution.
        """
        resource = self.get_resource(resource_id)
        if resource is None:
            return self

        updated_resource = resource.remove_task(task_id)

        new_resource_profiles = [
            resource_profile.remove_resource(resource_id)
            if resource_profile.id == task_id
            else resource_profile.update_resource(updated_resource)
            for resource_profile in self.resource_profiles
        ]

        new_task_resource_distribution = [
            task_resource_distribution.remove_resource(resource_id)
            if task_resource_distribution.task_id == task_id
            else task_resource_distribution
            for task_resource_distribution in self.task_resource_distribution
        ]

        return replace(
            self,
            resource_profiles=new_resource_profiles,
            task_resource_distribution=new_task_resource_distribution,
        )

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

    def _clone_resource_calendars(
        self, original: Resource, clone: Resource, _: list[str]
    ):
        """Get a Clone of the Resource Calendars, with the new resource added."""
        original_resource_calendar = self.get_calendar(original.calendar)
        if original_resource_calendar is None:
            return self.resource_calendars

        return self.resource_calendars + [
            replace(
                original_resource_calendar,
                id=clone.calendar,
                name=clone.calendar,
            )
        ]

    def _clone_task_distributions(
        self,
        original: Resource,
        clone: Resource,
        assigned_tasks: list[str],
    ):
        """Get a Clone of the Task Distributions, with the new resource added."""
        original_task_distributions = [
            self.get_task_resource_distribution(task_id) for task_id in assigned_tasks
        ]

        new_task_distributions = [
            task_distribution.add_resource_based_on_original(original.id, clone.id)
            for task_distribution in self.task_resource_distribution
            if task_distribution in original_task_distributions
        ]

        return [
            task_distribution
            for task_distribution in self.task_resource_distribution
            if task_distribution not in original_task_distributions
        ] + new_task_distributions

    def _clone_resource_profiles(
        self, _: Resource, clone: Resource, assigned_tasks: list[str]
    ):
        """Get a Clone of the Resource Profiles, with the new resource added."""
        original_resource_profiles = [
            self.get_resource_profile(task) for task in assigned_tasks
        ]

        new_resource_profiles = [
            replace(
                resource_profile,
                resource_list=resource_profile.resource_list + [clone],
            )
            for resource_profile in original_resource_profiles
            if resource_profile is not None
        ]

        return [
            resource_profile
            for resource_profile in self.resource_profiles
            if resource_profile not in original_resource_profiles
        ] + new_resource_profiles
