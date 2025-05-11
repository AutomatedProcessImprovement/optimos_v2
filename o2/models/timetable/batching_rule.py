from collections import defaultdict
from dataclasses import asdict, dataclass, replace
from json import dumps
from typing import Literal, Optional, Union

from dataclass_wizard import JSONWizard
from sympy import Symbol, lambdify

from o2.models.days import DAY
from o2.models.legacy_constraints import WorkMasks
from o2.models.rule_selector import RuleSelector
from o2.models.settings import Settings
from o2.models.timetable.batch_type import BATCH_TYPE
from o2.models.timetable.distribution import Distribution
from o2.models.timetable.firing_rule import (
    FiringRule,
    OrRules,
    rule_is_daily_hour,
    rule_is_size,
    rule_is_week_day,
)
from o2.models.timetable.rule_type import RULE_TYPE
from o2.models.timetable.time_period import TimePeriod
from o2.util.helper import hash_string


@dataclass(frozen=True)
class BatchingRule(JSONWizard):
    """Rules for when and how to batch tasks."""

    task_id: str
    type: BATCH_TYPE
    size_distrib: list[Distribution]
    duration_distrib: list[Distribution]
    firing_rules: OrRules

    def __post_init__(self) -> None:
        """Post-init hook to create a normalized representation of the firing rules."""
        if not Settings.CHECK_FOR_TIMETABLE_EQUALITY:
            return
        # Create a normalized representation:
        #  - Each inner list is sorted (ignoring its original order)
        #  - The collection of rows is also sorted so that their order doesn't matter.
        # Using tuple of tuples makes it hashable.
        normalized = tuple(sorted(tuple(sorted(row)) for row in self.firing_rules))  # type: ignore
        object.__setattr__(self, "_normalized", normalized)

    def __eq__(self, other: object) -> bool:
        """Check if two batching rules are equal."""
        if not Settings.CHECK_FOR_TIMETABLE_EQUALITY:
            return isinstance(other, BatchingRule) and (
                self.task_id,
                self.type,
                self.size_distrib,
                self.duration_distrib,
                self.firing_rules,
            ) == (
                other.task_id,
                other.type,
                other.size_distrib,
                other.duration_distrib,
                other.firing_rules,
            )
        if not isinstance(other, BatchingRule):
            return NotImplemented

        # TODO: This is due to some timetable objects being pickled before the normalization implementation.
        if "_normalized" not in self.__dict__:
            normalized = tuple(sorted(tuple(sorted(row)) for row in self.firing_rules))  # type: ignore
            object.__setattr__(self, "_normalized", normalized)

        if "_normalized" not in other.__dict__:
            normalized = tuple(sorted(tuple(sorted(row)) for row in other.firing_rules))  # type: ignore
            object.__setattr__(other, "_normalized", normalized)

        return (
            self._normalized == other._normalized  # type: ignore
            and self.task_id == other.task_id
            and self.type == other.type
            and self.size_distrib == other.size_distrib
            and self.duration_distrib == other.duration_distrib
        )

    def __hash__(self) -> int:
        """Hash the batching rule."""
        if not Settings.CHECK_FOR_TIMETABLE_EQUALITY:
            return hash(
                (
                    self.task_id,
                    self.type,
                    self.size_distrib,
                    self.duration_distrib,
                    self.firing_rules,
                )
            )
        return hash(
            (
                self.task_id,
                self.type,
                self.size_distrib,
                self.duration_distrib,
                self._normalized,  # type: ignore
            )
        )

    def id(self) -> str:
        """Generate a unique hash identifier for this batching rule.

        Creates a string hash based on the serialized representation of this rule.
        """
        return hash_string(str(dumps(asdict(self))).encode())

    def get_firing_rule_selectors(self, type: Optional[RULE_TYPE] = None) -> list["RuleSelector"]:
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
        tuple[Optional["RuleSelector"], "RuleSelector", "RuleSelector"],
        tuple[Optional[DAY], int, int],
    ]:
        """Get the time period for daily hour firing rules.

        Returns a dictionary with the optional Rule Selector of the day,
        lower bound, and upper bound as the key,
        and the day, lower bound, and upper bound as the value.
        """
        time_periods_by_or_index = {}
        for or_index, or_rules in enumerate(self.firing_rules):
            day_selector = None
            lower_bound_selector = None
            upper_bound_selector = None
            day = None
            lower_bound = float("-inf")
            upper_bound = float("inf")
            for and_rule_index, and_rule in enumerate(or_rules):
                if rule_is_week_day(and_rule):
                    day_selector = RuleSelector.from_batching_rule(self, (or_index, and_rule_index))
                    day = and_rule.value
                if rule_is_daily_hour(and_rule):
                    if and_rule.is_lt_or_lte:
                        if upper_bound is None or and_rule.value < upper_bound:
                            upper_bound = and_rule.value
                            upper_bound_selector = RuleSelector.from_batching_rule(
                                self, (or_index, and_rule_index)
                            )
                    elif and_rule.is_gt_or_gte and (lower_bound is None or and_rule.value > lower_bound):
                        lower_bound = and_rule.value
                        lower_bound_selector = RuleSelector.from_batching_rule(
                            self, (or_index, and_rule_index)
                        )
            time_periods_by_or_index[(day_selector, lower_bound_selector, upper_bound_selector)] = (
                day,
                lower_bound,
                upper_bound,
            )
        return time_periods_by_or_index

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
            return all(rule.attribute != RULE_TYPE.DAILY_HOUR for rule in self.firing_rules[or_index])
        return True

    def remove_firing_rule(self, rule_selector: "RuleSelector") -> "Optional[BatchingRule]":
        """Remove a firing rule. Returns a new BatchingRule."""
        assert rule_selector.firing_rule_index is not None
        or_index = rule_selector.firing_rule_index[0]
        and_index = rule_selector.firing_rule_index[1]
        if or_index >= len(self.firing_rules):
            return None
        if and_index >= len(self.firing_rules[or_index]):
            return None
        and_rules = self.firing_rules[or_index][:and_index] + self.firing_rules[or_index][and_index + 1 :]

        if len(and_rules) == 0:
            or_rules = self.firing_rules[:or_index] + self.firing_rules[or_index + 1 :]
        else:
            or_rules = self.firing_rules[:or_index] + [and_rules] + self.firing_rules[or_index + 1 :]

        if len(or_rules) == 0:
            return None
        return replace(self, firing_rules=or_rules)

    def generate_distrib(self, duration_fn: str) -> "BatchingRule":
        """Regenerate the duration and size distributions.

        Looks at every size rule and then will create a new duration distribution
        based on every size specified.
        E.g. if there is a size rule with <= 10, then it will create a new distribution for 1-10.

        It will not touch the existing duration distribution, it will only add new distributions
        """
        sizes = set()
        for and_rules in self.firing_rules:
            for rule in and_rules:
                if rule.attribute != RULE_TYPE.SIZE:
                    continue
                if rule.is_eq:
                    sizes.add(rule.value)
                elif rule.is_gte:
                    sizes.add(range(rule.value, 101))
                elif rule.is_gt:
                    sizes.add(range(rule.value + 1, 101))
                elif rule.is_lte:
                    sizes.add(range(1, rule.value + 1))
                elif rule.is_lt:
                    sizes.add(range(1, rule.value))

        new_duration_distrib = []
        new_size_distrib = []
        duration_lambda = lambdify(Symbol("size"), duration_fn)
        for size in sizes:
            new_duration_distrib.append(Distribution(key=str(size), value=duration_lambda(size)))
        for size in sizes:
            new_size_distrib.append(Distribution(key=str(size), value=1))
        # Special case: if 1 is not in sizes, remove any distribution that has 1 as a key
        # and add a new one with value 0
        if 1 not in sizes:
            new_size_distrib = [distribution for distribution in new_size_distrib if distribution.key != "1"]
            new_size_distrib.append(Distribution(key="1", value=0))

        return replace(self, duration_distrib=new_duration_distrib, size_distrib=new_size_distrib)

    def replace_firing_rule(
        self,
        rule_selector: "RuleSelector",
        new_rule: FiringRule,
        skip_merge: bool = False,
        duration_fn: Optional[str] = None,
    ) -> "BatchingRule":
        """Replace a firing rule. Returns a new BatchingRule."""
        assert rule_selector.firing_rule_index is not None
        or_index = rule_selector.firing_rule_index[0]
        and_index = rule_selector.firing_rule_index[1]
        if or_index >= len(self.firing_rules) or and_index >= len(self.firing_rules[or_index]):
            return self
        and_rules = (
            self.firing_rules[or_index][:and_index]
            + [new_rule]
            + self.firing_rules[or_index][and_index + 1 :]
        )

        or_rules = self.firing_rules[:or_index] + [and_rules] + self.firing_rules[or_index + 1 :]

        updated_batching_rule = replace(self, firing_rules=or_rules)
        if duration_fn is not None:
            updated_batching_rule = updated_batching_rule.generate_distrib(duration_fn)

        if (
            not skip_merge
            and new_rule.attribute == RULE_TYPE.WEEK_DAY
            or new_rule.attribute == RULE_TYPE.DAILY_HOUR
        ):
            return updated_batching_rule._generate_merged_datetime_firing_rules()
        return updated_batching_rule

    def add_firing_rule(self, firing_rule: FiringRule) -> "BatchingRule":
        """Add a firing rule. Returns a new BatchingRule."""
        updated_batching_rule = replace(self, firing_rules=self.firing_rules + [[firing_rule]])
        if firing_rule.attribute == RULE_TYPE.WEEK_DAY or firing_rule.attribute == RULE_TYPE.DAILY_HOUR:
            return updated_batching_rule._generate_merged_datetime_firing_rules()
        return updated_batching_rule

    def add_firing_rules(self, firing_rules: list[FiringRule]) -> "BatchingRule":
        """Add a list of firing rules. Returns a new BatchingRule."""
        updated_batching_rule = replace(self, firing_rules=self.firing_rules + [firing_rules])
        if any(
            rule.attribute == RULE_TYPE.WEEK_DAY or rule.attribute == RULE_TYPE.DAILY_HOUR
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
        size_dict: dict[Union[DAY, Literal["ALL"]], dict[int, int]] = defaultdict(dict)

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
                        size_dict[week_day_rule.value].get(daily_hour_gte_rule.value, 0),
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
        self, size_dict: dict[Union[DAY, Literal["ALL"]], dict[int, int]], period: TimePeriod
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
         - if there is more than 1 (single) size rule
        """
        has_single_size_rule = False
        for and_rules in self.firing_rules:
            # OR rules should not be duplicated
            largest_smaller_than_time = None
            smallest_larger_than_time = None
            # Duplicate rules are not allowed
            if self.firing_rules.count(and_rules) > 1:
                return False
            if len(and_rules) == 0:
                # Empty AND rules are not allowed
                return False
            if len(and_rules) == 1 and rule_is_size(and_rules[0]) and and_rules[0].is_gte:
                if has_single_size_rule:
                    return False
                has_single_size_rule = True
            has_daily_hour_rule = False
            for rule in and_rules:
                if and_rules.count(rule) > 1:
                    return False
                if rule_is_daily_hour(rule):
                    if rule.is_lt_or_lte and (
                        largest_smaller_than_time is None or rule.value > largest_smaller_than_time
                    ):
                        largest_smaller_than_time = rule.value
                    elif rule.is_gt_or_gte and (
                        smallest_larger_than_time is None or rule.value < smallest_larger_than_time
                    ):
                        smallest_larger_than_time = rule.value
                    has_daily_hour_rule = True
                if rule_is_week_day(rule) and has_daily_hour_rule:
                    return False

            if (
                largest_smaller_than_time is not None
                and smallest_larger_than_time is not None
                and smallest_larger_than_time >= largest_smaller_than_time
            ):
                return False

        return True

    @staticmethod
    def from_task_id(
        task_id: str,
        type: BATCH_TYPE = BATCH_TYPE.PARALLEL,
        firing_rules: list[FiringRule] = [],  # noqa: B006
        size: Optional[int] = None,
        duration_fn: Optional[str] = None,
    ) -> "BatchingRule":
        """Create a BatchingRule from a task id.

        NOTE: Setting `size` to a value will limit the new rule to only
        this size. You can omit it, to support batches up to 50.
        TODO: Get limit from constraints
        """
        duration_lambda = lambdify(Symbol("size"), duration_fn if duration_fn else "size")
        size_distrib = ([Distribution(key=str(1), value=0.0)] if size != 1 else []) + (
            [Distribution(key=str(new_size), value=1.0) for new_size in range(2, 50)]
            if size is None
            else [Distribution(key=str(size), value=1.0)]
        )
        duration_distrib = (
            [Distribution(key=str(new_size), value=duration_lambda(new_size)) for new_size in range(1, 50)]
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
