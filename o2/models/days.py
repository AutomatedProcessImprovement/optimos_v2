from enum import Enum


class DAY(str, Enum):
    """The days of the week."""

    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"


DAYS = [
    DAY.MONDAY,
    DAY.TUESDAY,
    DAY.WEDNESDAY,
    DAY.THURSDAY,
    DAY.FRIDAY,
    DAY.SATURDAY,
    DAY.SUNDAY,
]


def day_range(start: DAY, end: DAY) -> list[DAY]:
    """Get the range of days between two days."""
    start_idx = DAYS.index(start)
    end_idx = DAYS.index(end)
    return DAYS[start_idx : end_idx + 1]


def is_day_in_range(day: DAY, start: DAY, end: DAY) -> bool:
    """Check if a day is in a range of days."""
    return DAYS.index(start) <= DAYS.index(day) <= DAYS.index(end)
