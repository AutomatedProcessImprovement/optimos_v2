"""Resource class for modeling personnel, machines, or other resources."""

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from dataclass_wizard import JSONWizard

from o2.util.helper import CLONE_REGEX, random_string

if TYPE_CHECKING:
    from o2.models.timetable.timetable_type import TimetableType


@dataclass(frozen=True)
class Resource(JSONWizard):
    """Represents a resource such as a person, machine, or other entity that performs tasks."""

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
