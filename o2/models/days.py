from datetime import datetime
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

    def next_day(self) -> "DAY":
        """Get the next day."""
        index = DAYS.index(self)
        return DAYS[(index + 1) % len(DAYS)]

    def previous_day(self) -> "DAY":
        """Get the previous day."""
        index = DAYS.index(self)
        return DAYS[(index - 1) % len(DAYS)]

    @staticmethod
    def from_weekday(weekday: int) -> "DAY":
        """Get the day from the weekday (e.g from datetime.weekday())."""
        return DAYS[weekday]

    @staticmethod
    def from_date(date: datetime) -> "DAY":
        """Get the day from the date."""
        return DAY.from_weekday(date.weekday())


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
