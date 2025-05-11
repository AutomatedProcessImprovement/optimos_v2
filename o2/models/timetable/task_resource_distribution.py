"""Classes for defining distributions of resources to tasks and arrival times."""

from dataclasses import dataclass, replace
from functools import cached_property
from itertools import groupby
from operator import itemgetter
from typing import TYPE_CHECKING, Optional

from dataclass_wizard import JSONWizard

from o2.models.days import DAY
from o2.models.timetable.distribution_parameter import DistributionParameter
from o2.models.timetable.distribution_type import DISTRIBUTION_TYPE
from o2.models.timetable.time_period import TimePeriod
from o2.util.bit_mask_helper import find_most_frequent_overlap

if TYPE_CHECKING:
    from o2.models.timetable.timetable_type import TimetableType


@dataclass(frozen=True)
class ArrivalTimeDistribution(JSONWizard):
    """Distribution for arrival times of cases."""

    distribution_name: DISTRIBUTION_TYPE
    distribution_params: list[DistributionParameter]


@dataclass(frozen=True)
class TaskResourceDistribution(JSONWizard):
    """Distribution parameters for a specific resource assigned to a task."""

    resource_id: str
    distribution_name: str
    distribution_params: list[DistributionParameter]


@dataclass(frozen=True)
class TaskResourceDistributions(JSONWizard):
    """Collection of resource distributions for a specific task."""

    task_id: str
    resources: list[TaskResourceDistribution]

    def remove_resource(self, resource_id: str) -> "TaskResourceDistributions":
        """Remove a resource from the distribution."""
        return replace(
            self,
            resources=[resource for resource in self.resources if resource.resource_id != resource_id],
        )

    def add_resource(self, distribution: TaskResourceDistribution) -> "TaskResourceDistributions":
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
            (resource for resource in self.resources if resource.resource_id == original_resource_id),
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
        resources_assigned_to_task = timetable.get_resources_assigned_to_task(self.task_id)
        calendars = [timetable.get_calendar_for_resource(resource) for resource in resources_assigned_to_task]
        bitmasks_by_day = [
            bitmask for calendar in calendars if calendar is not None for bitmask in calendar.bitmasks_by_day
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
