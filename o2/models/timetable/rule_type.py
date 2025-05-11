"""RULE_TYPE enum for defining types of batching rules."""

from enum import Enum


class RULE_TYPE(str, Enum):  # noqa: N801, D101
    READY_WT = "ready_wt"
    LARGE_WT = "large_wt"
    DAILY_HOUR = "daily_hour"
    WEEK_DAY = "week_day"
    SIZE = "size"
