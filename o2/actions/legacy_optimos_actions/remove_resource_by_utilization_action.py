from dataclasses import dataclass
from typing import Literal

from o2.actions.base_actions.base_action import RateSelfReturnType
from o2.actions.base_actions.modify_resource_base_action import (
    ModifyResourceBaseAction,
    ModifyResourceBaseActionParamsType,
)
from o2.models.self_rating import RATING, SelfRatingInput
from o2.store import Store


class RemoveResourceByUtilizationActionParamsType(ModifyResourceBaseActionParamsType):
    """Parameter for `RemoveResourceByUtilizationAction`."""


@dataclass(frozen=True)
class RemoveResourceByUtilizationAction(ModifyResourceBaseAction, str=False):
    """`RemoveResourceByUtilizationAction` will remove the most unutilized resource.

    This action is based on the original optimos implementation,
    see `resolve_remove_resources_in_process` in that project.

    It first gets all resources sorted by their utilization (ascending)
    then it removes the resource with the lowest utilization, if that resource's tasks
    can be done by other resources.
    """

    @staticmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        """Generate a best set of parameters & self-evaluates this action."""
        timetable = store.solution.state.timetable
        resources = input.parent_evaluation.get_least_utilized_resources()
        for resource_id in resources:
            resource = timetable.get_resource(resource_id)
            if resource is None or not resource.can_safely_be_removed(timetable):
                continue
            yield (
                RemoveResourceByUtilizationAction.get_default_rating(store),
                RemoveResourceByUtilizationAction(
                    RemoveResourceByUtilizationActionParamsType(
                        resource_id=resource_id,
                        remove_resource=True,
                    )
                ),
            )

        return
