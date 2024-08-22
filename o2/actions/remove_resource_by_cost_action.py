from dataclasses import dataclass
from typing import Literal

from o2.actions.modify_resource_base_action import (
    ModifyResourceBaseAction,
    ModifyResourceBaseActionParamsType,
)
from o2.models.self_rating import RATING, SelfRatingInput
from o2.store import Store
from o2.actions.base_action import RateSelfReturnType


class RemoveResourceByCostActionParamsType(ModifyResourceBaseActionParamsType):
    """Parameter for `RemoveResourceByCostAction`."""


@dataclass(frozen=True)
class RemoveResourceByCostAction(ModifyResourceBaseAction):
    """`RemoveResourceByCostAction` will remove the resource with the highest cost.

     This action is based on the original optimos implementation,
    see `resolve_remove_resources_in_process` in that project.

    It first gets all resources sorted by their cost (cost/hour * available_time),
    then it removes the resource with the highest cost, if that resource's tasks
    can be done by other resources.
    """

    @staticmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        """Generate a best set of parameters & self-evaluates this action."""
        resources = store.state.timetable.get_resources_with_cost()
        for resource, _cost in resources:
            if not resource.can_safely_be_removed(store.state.timetable):
                continue
            yield (
                RemoveResourceByCostAction.get_default_rating(store),
                RemoveResourceByCostAction(
                    RemoveResourceByCostActionParamsType(
                        resource_id=resource.id,
                        remove_resource=True,
                    )
                ),
            )

        return
