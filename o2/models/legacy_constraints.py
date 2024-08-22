import operator
from dataclasses import dataclass
from functools import reduce
from typing import TYPE_CHECKING, List, Optional, TypedDict, Union

from dataclass_wizard import JSONWizard

from o2.models.days import DAY

if TYPE_CHECKING:
    from o2.models.timetable import ResourceCalendar, TimetableType


@dataclass(frozen=True)
class WorkMasks(JSONWizard):
    """Bitmask per day."""

    monday: Optional[int] = 0
    tuesday: Optional[int] = 0
    wednesday: Optional[int] = 0
    thursday: Optional[int] = 0
    friday: Optional[int] = 0
    saturday: Optional[int] = 0
    sunday: Optional[int] = 0

    def get(self, day: DAY) -> int:
        """Get the mask for a specific day."""
        return getattr(self, day.name.lower()) or 0

    def has_intersection(self, calendar: "ResourceCalendar") -> bool:
        """Check if the calendar has an overlap (intersection) with the work masks."""
        for day, periods in calendar.split_group_by_day():
            masks = [period.to_bitmask() for period in periods]
            day_mask = reduce(operator.or_, masks)
            if day_mask & self.get(day):
                return True
        return False

    def is_super_set(self, calendar: "ResourceCalendar") -> bool:
        """Check if the work masks are a super set of the calendar."""
        for day, periods in calendar.split_group_by_day():
            masks = [period.to_bitmask() for period in periods]
            day_mask = reduce(operator.or_, masks)
            if day_mask & ~self.get(day):
                return False
        return True

    def is_subset(self, calendar: "ResourceCalendar") -> bool:
        """Check if the work masks are a subset of the calendar."""
        for day, periods in calendar.split_group_by_day():
            masks = [period.to_bitmask() for period in periods]
            day_mask = reduce(operator.or_, masks)
            if ~day_mask & self.get(day):
                return False
        return True


@dataclass(frozen=True)
class GlobalConstraints(JSONWizard):
    """'Global' constraints for a resource, independent of the day."""

    max_weekly_cap: float
    max_daily_cap: float
    max_consecutive_cap: float
    max_shifts_day: int
    max_shifts_week: float
    is_human: bool

    def verify_timetable(self, calendar: "ResourceCalendar") -> bool:
        """Check if the timetable is valid against the constraints."""
        return (
            calendar.total_hours <= self.max_weekly_cap
            and calendar.max_hours_per_day <= self.max_daily_cap
            and calendar.max_consecutive_hours <= self.max_consecutive_cap
            and calendar.max_periods_per_day <= self.max_shifts_day
            and calendar.total_periods <= self.max_shifts_week
        )


@dataclass(frozen=True)
class ResourceConstraints(JSONWizard):
    """Constraints for a resource."""

    global_constraints: GlobalConstraints
    never_work_masks: WorkMasks
    always_work_masks: WorkMasks


@dataclass(frozen=True)
class ConstraintsResourcesItem(JSONWizard):
    """Resource constraints for a specific resource."""

    id: str
    constraints: ResourceConstraints

    def verify_timetable(self, timetable: "TimetableType") -> bool:
        """Check if the timetable is valid against the constraints."""
        original_calendar = timetable.get_calendar_for_resource(self.id)
        calendars = timetable.get_calendars_for_resource_clones(self.id)
        if original_calendar is not None:
            calendars.append(original_calendar)
        return all(self._verify_calendar(calendar) for calendar in calendars)

    def _verify_calendar(self, calendar: "ResourceCalendar") -> bool:
        return (
            self.constraints.global_constraints.verify_timetable(calendar)
            and not self.constraints.never_work_masks.has_intersection(calendar)
            and self.constraints.always_work_masks.is_subset(calendar)
        )
