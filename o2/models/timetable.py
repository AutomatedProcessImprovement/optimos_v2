import hashlib
from collections import defaultdict
from collections.abc import Iterator
from dataclasses import asdict, dataclass, field, replace
from enum import Enum
from functools import cached_property, reduce
from itertools import groupby
from json import dumps
from operator import itemgetter
from typing import (
    TYPE_CHECKING,
    Generic,
    Literal,
    Optional,
    TypeGuard,
    TypeVar,
    Union,
)

from dataclass_wizard import JSONWizard
from sympy import Symbol, lambdify

from o2.models.legacy_constraints import WorkMasks
from o2.models.rule_selector import RuleSelector
from o2.models.time_period import TimePeriod
from o2.util.bit_mask_helper import (
    any_has_overlap,
    find_mixed_ranges_in_bitmask,
    find_most_frequent_overlap,
)
from o2.util.custom_dumper import CustomDumper, CustomLoader
from o2.util.helper import (
    CLONE_REGEX,
    hash_int,
    hash_string,
    name_is_clone_of,
    random_string,
)
from o2.util.logger import info

if TYPE_CHECKING:
    from o2.models.constraints import ConstraintsType
    from o2.models.state import State
    from o2.store import Store

import operator

from o2.models.days import DAY, is_day_in_range


class BATCH_TYPE(str, Enum):  # noqa: D101, N801
    SEQUENTIAL = "Sequential"  # one after another
    CONCURRENT = "Concurrent"  # tasks are in progress simultaneously
    # (executor changes the context between different tasks)
    PARALLEL = "Parallel"  # tasks are being executed simultaneously


class RULE_TYPE(str, Enum):  # noqa: N801, D101
    READY_WT = "ready_wt"
    LARGE_WT = "large_wt"
    DAILY_HOUR = "daily_hour"
    WEEK_DAY = "week_day"
    SIZE = "size"


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
    UNIFORM = "uniform"

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
    assigned_tasks: list[str]

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

    def clone(self, assigned_tasks: list[str]) -> "Resource":
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
    resource_list: list[Resource]
    fixed_cost_fn: str = "0"

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
    distribution_params: list[DistributionParameter]


@dataclass(frozen=True)
class Probability(JSONWizard):
    path_id: str
    value: float


@dataclass(frozen=True)
class GatewayBranchingProbability(JSONWizard):
    gateway_id: str
    probabilities: list[Probability]


@dataclass(frozen=True)
class TaskResourceDistribution(JSONWizard):
    resource_id: str
    distribution_name: str
    distribution_params: list[DistributionParameter]


@dataclass(frozen=True)
class TaskResourceDistributions(JSONWizard):
    task_id: str
    resources: list[TaskResourceDistribution]

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

    def get_highest_availability_time_period(
        self, timetable: "TimetableType", min_hours: int
    ) -> Optional[TimePeriod]:
        """Get the highest availability time period for the task.

        The highest availability time period is the time period with the highest
        frequency of availability.
        If no overlapping time periods is found, it will return the longest non-overlapping
        time period.
        """
        resources_assigned_to_task = timetable.get_resources_assigned_to_task(
            self.task_id
        )
        calendars = [
            timetable.get_calendar_for_resource(resource)
            for resource in resources_assigned_to_task
        ]
        bitmasks_by_day = [
            bitmask
            for calendar in calendars
            if calendar is not None
            for bitmask in calendar.bitmasks_by_day
        ]
        if len(bitmasks_by_day) == 0:
            return None

        bitmasks_sorted_by_day = sorted(bitmasks_by_day, key=itemgetter(0))
        bitmasks_grouped_by_day = groupby(bitmasks_sorted_by_day, key=itemgetter(0))
        max_frequency = 0
        max_size = 0
        result = None
        for day, bitmask_pairs in bitmasks_grouped_by_day:
            bitmasks = [pair[1] for pair in bitmask_pairs]
            overlap = find_most_frequent_overlap(bitmasks, min_size=min_hours)
            if overlap is None:
                continue
            frequency, start, stop = overlap

            size = stop - start
            if frequency > max_frequency and size > max_size:
                max_frequency = frequency
                max_size = size
                result = TimePeriod.from_start_end(start, stop, day)

        return result

    @cached_property
    def resource_ids(self) -> list[str]:
        """Get the resource ids in the distribution."""
        return [resource.resource_id for resource in self.resources]


@dataclass(frozen=True)
class ResourceCalendar(JSONWizard, CustomLoader, CustomDumper):
    id: str
    name: str
    time_periods: list["TimePeriod"]

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

    def split_group_by_day(self) -> Iterator[tuple[DAY, Iterator["TimePeriod"]]]:
        """Split the time periods by day."""
        return groupby(self.split_time_periods_by_day(), key=lambda tp: tp.from_)

    def split_time_periods_by_day(self) -> list["TimePeriod"]:
        """Split the time periods by day and sort them."""
        return sorted(
            (tp for tp in self.time_periods for tp in tp.split_by_day()),
            key=lambda tp: tp.from_,
        )

    def get_periods_for_day(self, day: DAY) -> list["TimePeriod"]:
        """Get the time periods for a specific day."""
        return [tp for tp in self.split_time_periods_by_day() if tp.from_ == day]

    def get_periods_containing_day(self, day: DAY) -> list["TimePeriod"]:
        """Get the time periods that contain a specific day."""
        return [tp for tp in self.time_periods if is_day_in_range(day, tp.from_, tp.to)]

    @cached_property
    def work_masks(self) -> WorkMasks:
        """Convert the calendar to work masks."""
        days = {
            f"{day.name.lower()}": reduce(
                operator.or_, [tp.to_bitmask() for tp in time_periods]
            )
            for day, time_periods in self.split_group_by_day()
        }
        return WorkMasks(**days)

    def get_period_index_by_id(self, period_id: int) -> Optional[int]:
        """Get the index of a period by period id."""
        for i, tp in enumerate(self.time_periods):
            if tp.id == period_id:
                return i
        return None

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

    @cached_property
    def uid(self) -> int:
        """Get a unique identifier for the calendar."""
        return hash_int(self.to_json())

    def __hash__(self) -> int:
        return self.uid

    def replace_time_period(
        self, time_period_index: int, time_period: "TimePeriod"
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

    @cached_property
    def bitmasks_by_day(self) -> list[tuple[DAY, int]]:
        """Split the time periods by day and convert them to bitmasks.

        NOTE: This does not join overlapping/adjacent time periods.
        """
        return [(tp.from_, tp.to_bitmask()) for tp in self.split_time_periods_by_day()]

    def __str__(self) -> str:
        """Get a string representation of the calendar."""
        return (
            f"ResourceCalendar(id={self.id},\n"
            + ",\t\n".join(map(str, self.time_periods))
            + "\t\n)"
        )

    def get_time_periods_of_length_excl_idle(
        self,
        day: DAY,
        length: int,
        start_time: int,
        last_start_time: int,
    ) -> list["TimePeriod"]:
        """Get all time periods of a specific length.

        The time-periods will ignore any idle time.
        The result will be sorted by length, with shortest first,
        thereby sorting it by least idle time first.
        """
        bitmask = self.work_masks.get(day) or 0

        # # TODO Think about this
        # if last_start_time + length > 24:
        #     bitmask_tomorrow = bitmask_by_day.get(day.next_day()) or 0
        #     bitmask = bitmask << 24 | bitmask_tomorrow

        if bitmask == 0:
            return []

        ranges = find_mixed_ranges_in_bitmask(
            bitmask, length, start_time, last_start_time
        )

        ranges_sorted = sorted(ranges, key=lambda r: r[1] - r[0])

        return [
            TimePeriod.from_start_end(start, end, day) for start, end in ranges_sorted
        ]


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
        return hash_string(dumps(asdict(self)))

    @property
    def is_gte(self) -> bool:
        """Check if the rule is a greater than or equal rule."""
        return self.comparison == COMPARATOR.GREATER_THEN_OR_EQUAL

    @property
    def is_lt(self) -> bool:
        """Check if the rule is a less than rule."""
        return self.comparison == COMPARATOR.LESS_THEN

    @property
    def is_eq(self) -> bool:
        """Check if the rule is an equal rule."""
        return self.comparison == COMPARATOR.EQUAL

    @property
    def is_lte(self) -> bool:
        """Check if the rule is a less than or equal rule."""
        return self.comparison == COMPARATOR.LESS_THEN_OR_EQUAL

    @property
    def is_gt(self) -> bool:
        """Check if the rule is a greater than rule."""
        return self.comparison == COMPARATOR.GREATER_THEN

    @property
    def is_gt_or_gte(self) -> bool:
        """Check if the rule is a greater than or equal rule."""
        return self.is_gt or self.is_gte

    @property
    def is_lt_or_lte(self) -> bool:
        """Check if the rule is a less than or equal rule."""
        return self.is_lt or self.is_lte

    @staticmethod
    def eq(attribute: RULE_TYPE, value: V) -> "FiringRule[V]":
        return FiringRule(attribute=attribute, comparison=COMPARATOR.EQUAL, value=value)

    @staticmethod
    def gte(attribute: RULE_TYPE, value: V) -> "FiringRule[V]":
        return FiringRule(
            attribute=attribute,
            comparison=COMPARATOR.GREATER_THEN_OR_EQUAL,
            value=value,
        )

    @staticmethod
    def lt(attribute: RULE_TYPE, value: V) -> "FiringRule[V]":
        return FiringRule(
            attribute=attribute, comparison=COMPARATOR.LESS_THEN, value=value
        )

    @staticmethod
    def lte(attribute: RULE_TYPE, value: V) -> "FiringRule[V]":
        return FiringRule(
            attribute=attribute, comparison=COMPARATOR.LESS_THEN_OR_EQUAL, value=value
        )

    @staticmethod
    def gt(attribute: RULE_TYPE, value: V) -> "FiringRule[V]":
        return FiringRule(
            attribute=attribute, comparison=COMPARATOR.GREATER_THEN, value=value
        )


AndRules = list[FiringRule]
OrRules = list[AndRules]


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
    type: "BATCH_TYPE"
    size_distrib: list[Distribution]
    duration_distrib: list[Distribution]
    firing_rules: OrRules

    def id(self):
        # TODO Use a more performant hash function
        return hashlib.md5(str(dumps(asdict(self))).encode()).hexdigest()

    def get_firing_rule_selectors(
        self, type: Optional[RULE_TYPE] = None
    ) -> list["RuleSelector"]:
        """Get all firing rule selectors for the rule."""
        return [
            RuleSelector.from_batching_rule(self, (i, j))
            for i, or_rules in enumerate(self.firing_rules)
            for j, rule in enumerate(or_rules)
            if type is None or rule.attribute == type
        ]

    def get_time_period_for_daily_hour_firing_rules(
        self,
    ) -> dict[
        tuple[Optional[RuleSelector], RuleSelector, RuleSelector],
        tuple[Optional[DAY], int, int],
    ]:
        """Get the time period for daily hour firing rules.

        Returns a dictionary with the optional Rule Selector of the day, lower bound, and upper bound as the key,
        and the day, lower bound, and upper bound as the value.
        """
        timeperiods_by_or_index = {}
        for or_index, or_rules in enumerate(self.firing_rules):
            day_selector = None
            lower_bound_selector = None
            upper_bound_selector = None
            day = None
            lower_bound = float("-inf")
            upper_bound = float("inf")
            for and_rule_index, and_rule in enumerate(or_rules):
                if rule_is_week_day(and_rule):
                    day_selector = RuleSelector.from_batching_rule(
                        self, (or_index, and_rule_index)
                    )
                    day = and_rule.value
                if rule_is_daily_hour(and_rule):
                    if and_rule.is_lt_or_lte:
                        if upper_bound is None or and_rule.value < upper_bound:
                            upper_bound = and_rule.value
                            upper_bound_selector = RuleSelector.from_batching_rule(
                                self, (or_index, and_rule_index)
                            )
                    elif and_rule.is_gt_or_gte:
                        if lower_bound is None or and_rule.value > lower_bound:
                            lower_bound = and_rule.value
                            lower_bound_selector = RuleSelector.from_batching_rule(
                                self, (or_index, and_rule_index)
                            )
            timeperiods_by_or_index[
                (day_selector, lower_bound_selector, upper_bound_selector)
            ] = (day, lower_bound, upper_bound)
        return timeperiods_by_or_index

    def get_firing_rule(self, rule_selector: "RuleSelector") -> Optional[FiringRule]:
        """Get a firing rule by rule selector."""
        if rule_selector.firing_rule_index is None:
            return None
        or_index = rule_selector.firing_rule_index[0]
        and_index = rule_selector.firing_rule_index[1]
        if or_index >= len(self.firing_rules):
            return None
        if and_index >= len(self.firing_rules[or_index]):
            return None
        return self.firing_rules[or_index][and_index]

    def can_remove_firing_rule(self, or_index: int, and_index: int) -> bool:
        """Check if a firing rule can be removed.

        Checks:
        - We cannot remove a size rule from a DAILY_HOUR rule set.
        """
        if or_index >= len(self.firing_rules):
            return False
        if and_index >= len(self.firing_rules[or_index]):
            return False
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
        if or_index >= len(self.firing_rules):
            return None
        if and_index >= len(self.firing_rules[or_index]):
            return None
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
        self,
        rule_selector: "RuleSelector",
        new_rule: FiringRule,
        skip_merge: bool = False,
    ) -> "BatchingRule":
        """Replace a firing rule. Returns a new BatchingRule."""
        assert rule_selector.firing_rule_index is not None
        or_index = rule_selector.firing_rule_index[0]
        and_index = rule_selector.firing_rule_index[1]
        if or_index >= len(self.firing_rules) or and_index >= len(
            self.firing_rules[or_index]
        ):
            return self
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

        updated_batching_rule = replace(self, firing_rules=or_rules)

        if (
            not skip_merge
            and new_rule.attribute == RULE_TYPE.WEEK_DAY
            or new_rule.attribute == RULE_TYPE.DAILY_HOUR
        ):
            return updated_batching_rule._generate_merged_datetime_firing_rules()
        return updated_batching_rule

    def add_firing_rule(self, firing_rule: FiringRule) -> "BatchingRule":
        """Add a firing rule. Returns a new BatchingRule."""
        updated_batching_rule = replace(
            self, firing_rules=self.firing_rules + [[firing_rule]]
        )
        if (
            firing_rule.attribute == RULE_TYPE.WEEK_DAY
            or firing_rule.attribute == RULE_TYPE.DAILY_HOUR
        ):
            return updated_batching_rule._generate_merged_datetime_firing_rules()
        return updated_batching_rule

    def add_firing_rules(self, firing_rules: list[FiringRule]) -> "BatchingRule":
        """Add a list of firing rules. Returns a new BatchingRule."""
        updated_batching_rule = replace(
            self, firing_rules=self.firing_rules + [firing_rules]
        )
        if any(
            rule.attribute == RULE_TYPE.WEEK_DAY
            or rule.attribute == RULE_TYPE.DAILY_HOUR
            for rule in firing_rules
        ):
            return updated_batching_rule._generate_merged_datetime_firing_rules()
        return updated_batching_rule

    def _generate_merged_datetime_firing_rules(self) -> "BatchingRule":
        """Generate merged firing rules for datetime rules.

        E.g. if there are multiple OR-Rules, that only contain daily hour rules,
        we can merge them into a single OR-Rule. Or if there are multiple OR-Rules,
        that only contain the same week day + daily hour rule,
        we can merge them into a single OR-Rule.
        """

        or_rules_to_remove = []
        work_mask = WorkMasks()
        size_dict: dict[DAY | Literal["ALL"], dict[int, int]] = defaultdict(dict)

        for index, or_rules in enumerate(self.firing_rules):
            length = len(or_rules)
            if length > 4:
                continue
            daily_hour_gte_rule: Optional[FiringRule[int]] = None
            daily_hour_lt_rule: Optional[FiringRule[int]] = None
            week_day_rule: Optional[FiringRule[DAY]] = None
            size_rule: Optional[FiringRule[int]] = None

            for rule in or_rules:
                if rule_is_daily_hour(rule) and rule.is_gte:
                    daily_hour_gte_rule = rule
                elif rule_is_daily_hour(rule) and rule.is_lt:
                    daily_hour_lt_rule = rule
                elif rule_is_week_day(rule) and rule.is_eq:
                    week_day_rule = rule
                elif rule_is_size(rule) and rule.is_gt_or_gte:
                    size_rule = rule
            if daily_hour_gte_rule is None or daily_hour_lt_rule is None:
                continue
            if length == 4 and (size_rule is None or week_day_rule is None):
                continue
            if length == 3 and (week_day_rule is None and size_rule is None):
                continue
            if not week_day_rule:
                work_mask = work_mask.set_hour_range_for_every_day(
                    daily_hour_gte_rule.value,
                    daily_hour_lt_rule.value,
                )
                if size_rule:
                    size_dict["ALL"][daily_hour_gte_rule.value] = max(
                        size_dict["ALL"].get(daily_hour_gte_rule.value, 0),
                        size_rule.value,
                    )
            else:
                work_mask = work_mask.set_hour_range_for_day(
                    week_day_rule.value,
                    daily_hour_gte_rule.value,
                    daily_hour_lt_rule.value,
                )
                if size_rule:
                    size_dict[week_day_rule.value][daily_hour_gte_rule.value] = max(
                        size_dict[week_day_rule.value].get(
                            daily_hour_gte_rule.value, 0
                        ),
                        size_rule.value,
                    )
            or_rules_to_remove.append(index)
        new_or_rules = []
        for day in DAY:
            periods = TimePeriod.from_bitmask(work_mask.get(day), day)
            for period in periods:
                max_size = self._find_max_size(size_dict, period)
                rules = [
                    FiringRule.eq(RULE_TYPE.WEEK_DAY, day),
                    FiringRule.gte(RULE_TYPE.DAILY_HOUR, period.begin_time_hour),
                    FiringRule.lt(RULE_TYPE.DAILY_HOUR, period.end_time_hour),
                ]
                if max_size > 0:
                    rules.append(FiringRule.gte(RULE_TYPE.SIZE, max_size))
                new_or_rules.append(rules)
        return replace(
            self,
            firing_rules=new_or_rules
            + [
                or_rules
                for index, or_rules in enumerate(self.firing_rules)
                if index not in or_rules_to_remove
            ],
        )

    def _find_max_size(
        self, size_dict: dict[DAY | Literal["ALL"], dict[int, int]], period: TimePeriod
    ) -> int:
        all_entries = size_dict.get("ALL", {})
        day_entries = size_dict.get(period.from_, {})

        # Get maximum of all entries, that are between begin_time_hour and end_time_hour
        return max(
            max(all_entries.get(entry, 0), day_entries.get(entry, 0))
            for entry in range(period.begin_time_hour, period.end_time_hour)
        )

    def is_valid(self) -> bool:
        """Check if the timetable is valid.

        Currently this will check:
         - if daily hour rules come after week day rules
         - if there are no duplicate daily hour rules
        """
        for and_rules in self.firing_rules:
            # OR rules should not be duplicated
            largest_smaller_than_time = None
            smallest_larger_than_time = None
            if self.firing_rules.count(and_rules) > 1:
                return False
            if len(and_rules) == 0:
                # Empty AND rules are not allowed
                return False
            has_daily_hour_rule = False
            for rule in and_rules:
                if and_rules.count(rule) > 1:
                    return False
                if rule_is_daily_hour(rule):
                    if rule.is_lt_or_lte:
                        if (
                            largest_smaller_than_time is None
                            or rule.value > largest_smaller_than_time
                        ):
                            largest_smaller_than_time = rule.value
                    elif rule.is_gt_or_gte:
                        if (
                            smallest_larger_than_time is None
                            or rule.value < smallest_larger_than_time
                        ):
                            smallest_larger_than_time = rule.value
                    has_daily_hour_rule = True
                if rule_is_week_day(rule) and has_daily_hour_rule:
                    return False

            if (
                largest_smaller_than_time is not None
                and smallest_larger_than_time is not None
            ):
                if smallest_larger_than_time >= largest_smaller_than_time:
                    return False

        return True

    @staticmethod
    def from_task_id(
        task_id: str,
        type: "BATCH_TYPE" = BATCH_TYPE.PARALLEL,
        firing_rules: list[FiringRule] = [],
        size: Optional[int] = None,
        duration_fn: Optional[str] = None,
    ) -> "BatchingRule":
        """Create a BatchingRule from a task id."""
        duration_lambda = lambdify(
            Symbol("size"), duration_fn if duration_fn else "size"
        )
        size_distrib = ([Distribution(key=str(1), value=0.0)] if size != 1 else []) + (
            [Distribution(key=str(new_size), value=1.0) for new_size in range(2, 100)]
            if size is None
            else [Distribution(key=str(size), value=1.0)]
        )
        duration_distrib = (
            [
                Distribution(key=str(new_size), value=duration_lambda(new_size))
                for new_size in range(1, 100)
            ]
            if size is None
            else [Distribution(key=str(size), value=duration_lambda(size))]
        )
        return BatchingRule(
            task_id=task_id,
            type=type,
            size_distrib=size_distrib,
            duration_distrib=duration_distrib,
            firing_rules=[firing_rules],
        )


@dataclass(frozen=True)
class TimetableType(JSONWizard, CustomLoader, CustomDumper):
    resource_profiles: list[ResourcePool]
    arrival_time_distribution: ArrivalTimeDistribution
    arrival_time_calendar: list["TimePeriod"]
    gateway_branching_probabilities: list[GatewayBranchingProbability]
    task_resource_distribution: list[TaskResourceDistributions]
    resource_calendars: list[ResourceCalendar]
    event_distribution: EventDistribution
    batch_processing: list[BatchingRule] = field(default_factory=list)
    start_time: str = "2000-01-01T00:00:00Z"
    total_cases: int = 1000

    class _(JSONWizard.Meta):
        key_transform_with_dump = "SNAKE"

    def init_fixed_cost_fns(self, constraints: "ConstraintsType") -> "TimetableType":
        """Initialize the fixed cost fn for all resources."""
        return replace(
            self,
            resource_profiles=[
                replace(
                    resource_profile,
                    fixed_cost_fn=constraints.get_fixed_cost_fn_for_task(
                        resource_profile.id
                    ),
                )
                for resource_profile in self.resource_profiles
            ],
        )

    def get_batching_rule(
        self, rule_selector: "RuleSelector"
    ) -> Union[tuple[int, BatchingRule], tuple[None, None]]:
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

    def get_batching_rules_for_task(
        self, task_id: str, batch_type: Optional["BATCH_TYPE"] = None
    ) -> list[BatchingRule]:
        """Get all batching rules for a task."""
        return [
            rule
            for rule in self.batch_processing
            if rule.task_id == task_id
            and (batch_type is None or rule.type == batch_type)
        ]

    def get_batching_rules_for_tasks(
        self, task_ids: list[str], batch_type: Optional["BATCH_TYPE"] = None
    ) -> list[BatchingRule]:
        """Get all batching rules for a list of tasks."""
        return [
            rule
            for rule in self.batch_processing
            if rule.task_id in task_ids
            and (batch_type is None or rule.type == batch_type)
        ]

    def get_firing_rules_for_task(
        self,
        task_id: str,
        batch_type: Optional["BATCH_TYPE"] = None,
        rule_type: Optional[RULE_TYPE] = None,
    ) -> list[FiringRule]:
        """Get all firing rules for a task."""
        return [
            firing_rule
            for batching_rule in self.get_batching_rules_for_tasks(
                [task_id], batch_type
            )
            for firing_rules in batching_rule.firing_rules
            for firing_rule in firing_rules
            if rule_type is None or firing_rule.attribute == rule_type
        ]

    def get_longest_time_period_for_daily_hour_firing_rules(
        self, task_id: str, day: DAY
    ) -> Optional[tuple[Optional[RuleSelector], RuleSelector, RuleSelector]]:
        """Get the longest time period for daily hour firing rules.

        Returns the Rule Selector of the day, lower bound, and upper bound.
        """

        batching_rules = self.get_batching_rules_for_task(
            task_id=task_id,
        )

        best_selector = None
        best_length = 0

        for batching_rule in batching_rules:
            if batching_rule is None:
                continue
            periods = (
                batching_rule.get_time_period_for_daily_hour_firing_rules().items()
            )
            for (day_selector, lower_bound_selector, upper_bound_selector), (
                _day,
                lower_bound,
                upper_bound,
            ) in periods:
                if _day == day:
                    length = (
                        (upper_bound - lower_bound)
                        if upper_bound is not None and lower_bound is not None
                        else 0
                    )
                    if length > best_length:
                        best_selector = (
                            day_selector,
                            lower_bound_selector,
                            upper_bound_selector,
                        )
                        best_length = length
        return best_selector

    def get_firing_rule_selectors_for_task(
        self,
        task_id: str,
        batch_type: Optional["BATCH_TYPE"] = None,
        rule_type: Optional[RULE_TYPE] = None,
    ) -> list["RuleSelector"]:
        """Get all firing rule selectors for a task."""
        return [
            rule_selector
            for batching_rule in self.get_batching_rules_for_tasks(
                [task_id], batch_type
            )
            for rule_selector in batching_rule.get_firing_rule_selectors(rule_type)
        ]

    def get_firing_rules_for_tasks(
        self,
        task_ids: list[str],
        batch_type: Optional["BATCH_TYPE"] = None,
        rule_type: Optional[RULE_TYPE] = None,
    ) -> list[FiringRule]:
        """Get all firing rules for a list of tasks."""
        return [
            firing_rule
            for batching_rule in self.get_batching_rules_for_tasks(task_ids, batch_type)
            for firing_rules in batching_rule.firing_rules
            for firing_rule in firing_rules
            if rule_type is None or firing_rule.attribute == rule_type
        ]

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

    def get_tasks(self, resource_id: str) -> list[str]:
        """Get all tasks assigned to a resource."""
        resource = self.get_resource(resource_id)
        if resource is None:
            return []
        return resource.assigned_tasks

    def get_task_resource_distribution(
        self, task_id: str
    ) -> Optional[TaskResourceDistributions]:
        """Get task resource distribution by task id."""
        for task_resource_distribution in self.task_resource_distribution:
            if task_resource_distribution.task_id == task_id:
                return task_resource_distribution
        return None

    def get_resources_assigned_to_task(self, task_id: str) -> list[str]:
        """Get all resources assigned to a task."""
        task_resource_distribution = self.get_task_resource_distribution(task_id)
        if task_resource_distribution is None:
            return []
        return [
            resource.resource_id for resource in task_resource_distribution.resources
        ]

    def get_task_ids_assigned_to_resource(self, resource_id: str) -> list[str]:
        """Get all tasks assigned to a resource."""
        return [
            task_resource_distribution.task_id
            for task_resource_distribution in self.task_resource_distribution
            if resource_id in task_resource_distribution.resource_ids
        ]

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

    def get_hourly_rates(self) -> dict[str, int]:
        """Get the cost per hour for each resource."""
        return {
            resource.id: resource.cost_per_hour for resource in self.get_all_resources()
        }

    def get_fixed_cost_fns(self) -> dict[str, str]:
        """Get the fixed cost function for each resource pool (task)."""
        return {
            resource_profile.id: resource_profile.fixed_cost_fn
            for resource_profile in self.resource_profiles
        }

    def get_calendar_for_resource(
        self, resource_name: str
    ) -> Optional[ResourceCalendar]:
        """Get a resource calendar by resource name."""
        calendar_id = self.get_resource_calendar_id(resource_name)
        if calendar_id is None:
            return None
        return self.get_calendar(calendar_id)

    def get_calendar_for_base_resource(
        self, resource_name: str
    ) -> Optional[ResourceCalendar]:
        """Get a resource calendar by resource clone/original name.

        If the resource is a clone, get the calendar of the base resource.
        """
        return next(
            (
                self.get_calendar(resource.calendar)
                for resource in self.resource_profiles
                for resource in resource.resource_list
                if resource.name == resource_name
                or name_is_clone_of(resource_name, resource.name)
            ),
            None,
        )

    def get_calendars_for_resource_clones(
        self, resource_name: str
    ) -> list[ResourceCalendar]:
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

    def get_all_resources(self) -> list[Resource]:
        """Get all resources."""
        resources = {
            resource.id: resource
            for resource_profile in self.resource_profiles
            for resource in resource_profile.resource_list
        }
        return list(resources.values())

    def get_deleted_resources(self, base_state: "State") -> list[Resource]:
        """Get all resources that have been deleted."""
        return [
            resource
            for resource_profile in base_state.timetable.resource_profiles
            for resource in resource_profile.resource_list
            if self.get_resource(resource.id) is None
        ]

    def get_resources_with_cost(self) -> list[tuple[Resource, int]]:
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

    def replace_batching_rule(
        self, rule_selector: RuleSelector, new_batching_rule: BatchingRule
    ) -> "TimetableType":
        """Replace a batching rule."""
        return replace(
            self,
            batch_processing=[
                new_batching_rule
                if rule.task_id == rule_selector.batching_rule_task_id
                else rule
                for rule in self.batch_processing
            ],
        )

    def replace_firing_rule(
        self, rule_selector: RuleSelector, new_firing_rule: FiringRule
    ) -> "TimetableType":
        """Replace a firing rule."""
        _, batching_rule = self.get_batching_rule(rule_selector)
        if batching_rule is None:
            return self
        new_batching_rule = batching_rule.replace_firing_rule(
            rule_selector, new_firing_rule
        )
        return self.replace_batching_rule(rule_selector, new_batching_rule)

    def add_firing_rule(
        self,
        rule_selector: RuleSelector,
        new_firing_rule: FiringRule,
        duration_fn: Optional[str] = None,
    ) -> "TimetableType":
        """Add a firing rule."""
        _, old_batching_rule = self.get_batching_rule(rule_selector)
        if old_batching_rule is None:
            batching_rule = BatchingRule.from_task_id(
                rule_selector.batching_rule_task_id,
                firing_rules=[new_firing_rule],
                duration_fn=duration_fn,
            )
        else:
            batching_rule = old_batching_rule.add_firing_rule(new_firing_rule)
        return self.replace_batching_rule(rule_selector, batching_rule)

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
        self, resource_id: str, assigned_tasks: Optional[list[str]]
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
        if assigned_tasks is None:
            assigned_tasks = original_resource.assigned_tasks
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

    def get_task_ids(self) -> list[str]:
        """Get all task ids."""
        return [task.task_id for task in self.task_resource_distribution]

    def get_highest_availability_time_period(
        self, task_id: str, min_hours: int
    ) -> Optional[TimePeriod]:
        """Get the highest availability time period for the task.

        The highest availability time period is the time period with the highest
        frequency of availability.
        """
        task_distribution = self.get_task_resource_distribution(task_id)
        if task_distribution is None:
            return None
        return task_distribution.get_highest_availability_time_period(self, min_hours)

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

    @property
    def batching_rules_exist(self) -> bool:
        """Check if any batching rules exist."""
        return len(self.batch_processing) > 0

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

    def batching_rules_debug_str(self) -> str:
        """Get the batching rules as a string."""
        lines = []
        for batching_rule in self.batch_processing:
            lines.append(f"\tTask: {batching_rule.task_id}")
            or_lines = []
            for or_rule in batching_rule.firing_rules:
                and_lines = []
                for rule in or_rule:
                    and_lines.append(
                        f"\t\t{rule.attribute} {rule.comparison} {rule.value}\n"
                    )
                or_lines.append("\t\tAND\n".join(and_lines))
            lines.append("\tOR\n".join(or_lines))
        return "\n".join(lines)

    def print_batching_rules(self) -> None:
        """Print the batching rules."""
        info(self.batching_rules_debug_str())

    def is_valid(self) -> bool:
        """Check if the timetable is valid.

        The timetable is valid if all calendars are valid.
        TODO: Add more checks.
        """
        return all(calendar.is_valid() for calendar in self.resource_calendars) and all(
            rule.is_valid() for rule in self.batch_processing
        )
