from dataclasses import dataclass, replace

from dataclass_wizard import JSONWizard

from o2.models.timetable.resource import Resource


@dataclass(frozen=True)
class ResourcePool(JSONWizard):
    """Collection of resources that can be assigned to a task."""

    id: str
    name: str
    resource_list: list[Resource]
    fixed_cost_fn: str = "0"

    def remove_resource(self, resource_id: str) -> "ResourcePool":
        """Remove a resource from the pool."""
        return replace(
            self,
            resource_list=[resource for resource in self.resource_list if resource.id != resource_id],
        )

    def update_resource(self, updated_resource: Resource) -> "ResourcePool":
        """Update a resource in the pool."""
        return replace(
            self,
            resource_list=[
                updated_resource if updated_resource.id == resource.id else resource
                for resource in self.resource_list
            ],
        )
