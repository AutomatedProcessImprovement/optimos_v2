from dataclasses import dataclass
from typing import Literal

from o2.actions.base_action import RateSelfReturnType

from o2.actions.modify_resource_base_action import (
    ModifyResourceBaseAction,
    ModifyResourceBaseActionParamsType,
)
from o2.models.self_rating import RATING, SelfRatingInput
from o2.store import Store


class RemoveResourceByUtilizationActionParamsType(ModifyResourceBaseActionParamsType):
    """Parameter for `RemoveResourceByUtilizationAction`."""


@dataclass(frozen=True)
class RemoveResourceByUtilizationAction(ModifyResourceBaseAction):
    """`RemoveResourceByUtilizationAction` will remove the most unutilized resource.

    This action is based on the original optimos implementation,
    see `resolve_remove_resources_in_process` in that project.

    It first gets all resources sorted by their utilization (ascending)
    then it removes the resource with the lowest utilization.
    """

    @staticmethod
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        """Generate a best set of parameters & self-evaluates this action."""
        resources = input.base_evaluation.get_least_utilized_resources()
        for resource_id in resources:
            yield (
                RemoveResourceByUtilizationAction.DEFAULT_RATING,
                RemoveResourceByUtilizationAction(
                    RemoveResourceByUtilizationActionParamsType(
                        resource_id=resource_id,
                        remove_resource=True,
                    )
                ),
            )

        yield RATING.NOT_APPLICABLE, None
