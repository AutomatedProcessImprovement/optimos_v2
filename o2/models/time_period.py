from dataclasses import replace
from typing import TYPE_CHECKING, ClassVar, List, Optional

from pydantic import BaseModel, Field

from o2.models.days import DAY, day_range


class TimePeriod(BaseModel):
    """A Time Period in a resource calendar.

    Because `from` is a reserved keyword in Python, we use `from_` instead,
    this also means that we need to use pydantic directly instead of JSONWizard.
    """

    from_: "DAY" = Field(..., alias="from")
    """The start of the time period (day, uppercase, e.g. MONDAY)"""

    to: "DAY" = Field(...)
    """The end of the time period (day, uppercase, e.g. FRIDAY)"""

    begin_time: str = Field(..., alias="beginTime")
    """The start time of the time period (24h format, e.g. 08:00)"""
    end_time: str = Field(..., alias="endTime")
    """The end time of the time period (24h format, e.g. 17:00)"""

    class Config:  # noqa: D106
        frozen = True

    ALL_DAY_BITMASK: ClassVar[int] = 0b111111111111111111111111

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

        # return replace(
        #     self,
        #     begin_time=f"{new_begin:02}:{self.begin_time_minute:02}:{self.begin_time_second:02}",
        #     end_time=f"{new_end:02}:{self.end_time_minute:02}:{self.end_time_second:02}",
        # )
        return self.model_copy(
            update={
                "begin_time": f"{new_begin:02}:{self.begin_time_minute:02}:{self.begin_time_second:02}",
                "end_time": f"{new_end:02}:{self.end_time_minute:02}:{self.end_time_second:02}",
            }
        )

    def split_by_day(self) -> List["TimePeriod"]:
        """Split the time period by day.

        Return a list of time periods, one for each day in the range.
        """
        if self.is_empty:
            return []
        return [
            self.model_copy(update={"from_": day, "to": day})
            for day in day_range(self.from_, self.to)
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

    def __repr__(self) -> str:
        return (
            f"TimePeriod({self.from_},{self.begin_time} -> {self.to},{self.end_time})"
        )

    @staticmethod
    def from_bitmask(bitmask: int, day: "DAY") -> List["TimePeriod"]:
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
    def from_start_end(start: int, end: int, day: "DAY" = DAY.MONDAY) -> "TimePeriod":
        return TimePeriod(
            from_=day,
            to=day,
            begin_time=f"{start:02}:00:00",
            end_time=f"{end:02}:00:00",
        )

    @staticmethod
    def empty(day: "DAY" = DAY.MONDAY) -> "TimePeriod":
        return TimePeriod(
            from_=day,
            to=day,
            begin_time="00:00:00",
            end_time="00:00:00",
        )
