from dataclasses import asdict, dataclass
from json import dumps
from typing import Generic, Optional, TypeGuard, TypeVar

from dataclass_wizard import JSONWizard

from o2.models.days import DAY
from o2.models.timetable.comparator import COMPARATOR
from o2.models.timetable.rule_type import RULE_TYPE
from o2.util.helper import hash_string

V = TypeVar("V", DAY, int)


@dataclass(frozen=True, eq=True, order=True)
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
        """Create a FiringRule with an EQUAL comparison.

        Creates a rule that checks if an attribute equals the given value.
        """
        return FiringRule(attribute=attribute, comparison=COMPARATOR.EQUAL, value=value)

    @staticmethod
    def gte(attribute: RULE_TYPE, value: V) -> "FiringRule[V]":
        """Create a FiringRule with a GREATER_THAN_OR_EQUAL comparison.

        Creates a rule that checks if an attribute is greater than or equal to the given value.
        """
        return FiringRule(
            attribute=attribute,
            comparison=COMPARATOR.GREATER_THEN_OR_EQUAL,
            value=value,
        )

    @staticmethod
    def lt(attribute: RULE_TYPE, value: V) -> "FiringRule[V]":
        """Create a FiringRule with a LESS_THAN comparison.

        Creates a rule that checks if an attribute is less than the given value.
        """
        return FiringRule(attribute=attribute, comparison=COMPARATOR.LESS_THEN, value=value)

    @staticmethod
    def lte(attribute: RULE_TYPE, value: V) -> "FiringRule[V]":
        """Create a FiringRule with a LESS_THAN_OR_EQUAL comparison.

        Creates a rule that checks if an attribute is less than or equal to the given value.
        """
        return FiringRule(attribute=attribute, comparison=COMPARATOR.LESS_THEN_OR_EQUAL, value=value)

    @staticmethod
    def gt(attribute: RULE_TYPE, value: V) -> "FiringRule[V]":
        """Create a FiringRule with a GREATER_THAN comparison.

        Creates a rule that checks if an attribute is greater than the given value.
        """
        return FiringRule(attribute=attribute, comparison=COMPARATOR.GREATER_THEN, value=value)


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
