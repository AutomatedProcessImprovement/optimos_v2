"""ResourceCalendar class for defining work schedules."""

import operator
from collections.abc import Iterator
from dataclasses import dataclass, replace
from functools import cached_property, reduce
from itertools import groupby
from typing import Optional

from dataclass_wizard import JSONWizard

from o2.models.days import DAY, is_day_in_range
from o2.models.legacy_constraints import WorkMasks
from o2.models.timetable.time_period import TimePeriod
from o2.util.bit_mask_helper import any_has_overlap, find_mixed_ranges_in_bitmask
from o2.util.custom_dumper import CustomDumper, CustomLoader
from o2.util.helper import hash_int


@dataclass(frozen=True)
class ResourceCalendar(JSONWizard, CustomLoader, CustomDumper):
    """Defines a calendar of available time periods for a resource."""

    id: str
    name: str
    time_periods: list["TimePeriod"]
    workload_ratio: Optional[list["TimePeriod"]] = None

    def is_valid(self) -> bool:
        """Check if the calendar is valid.

        The calendar is valid if all time periods have a begin time before the end time.
        And if the time periods are not overlapping.
        """
        # We do not check for valid time periods if the time periods have a probability
        if any(tp.probability is not None for tp in self.time_periods):
            return True

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
            (tp for tp in self.time_periods for tp in tp.split_by_day),
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
            f"{day.name.lower()}": reduce(operator.or_, [tp.to_bitmask() for tp in time_periods])
            for day, time_periods in self.split_group_by_day()
        }
        return WorkMasks(**days)

    def get_period_index_by_id(self, period_id: str) -> Optional[int]:
        """Get the index of a period by period id."""
        for i, tp in enumerate(self.time_periods):
            if tp.id == period_id:
                return i
        return None

    @property
    def total_hours(self) -> int:
        """Get the total number of hours in the calendar."""
        return sum((tp.end_time_hour - tp.begin_time_hour) for tp in self.split_time_periods_by_day())

    @property
    def max_consecutive_hours(self) -> int:
        """Get the maximum number of continuous hours in the calendar."""
        return max((tp.end_time_hour - tp.begin_time_hour) for tp in self.time_periods)

    @property
    def max_periods_per_day(self) -> int:
        """Get the maximum number of periods in a day."""
        return max(len(list(tp.split_by_day)) for tp in self.time_periods)

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

    def replace_time_period(self, time_period_index: int, time_period: "TimePeriod") -> "ResourceCalendar":
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
                    tp for tp in old_time_period.split_by_day if tp.from_ != time_period.from_
                ]
                return replace(
                    self,
                    time_periods=self.time_periods[:time_period_index]
                    + new_time_periods
                    + self.time_periods[time_period_index + 1 :],
                )
        if old_time_period.from_ != time_period.from_ or old_time_period.to != time_period.to:
            # If the days are different, we need to split the time
            # periods by day, and only replace the time period
            # for the correct day.
            new_time_periods = time_period.split_by_day
            old_time_periods = old_time_period.split_by_day

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
        return f"ResourceCalendar(id={self.id},\n" + ",\t\n".join(map(str, self.time_periods)) + "\t\n)"

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

        ranges = find_mixed_ranges_in_bitmask(bitmask, length, start_time, last_start_time)

        ranges_sorted = sorted(ranges, key=lambda r: r[1] - r[0])

        return [TimePeriod.from_start_end(start, end, day) for start, end in ranges_sorted]
