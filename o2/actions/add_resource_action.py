from dataclasses import dataclass
from typing import Literal

from o2.actions.modify_resource_base_action import (
    ModifyResourceBaseAction,
    ModifyResourceBaseActionParamsType,
)
from o2.models.self_rating import RATING, SelfRatingInput
from o2.store import Store


class AddResourceActionParamsType(ModifyResourceBaseActionParamsType):
    """Parameter for `AddResourceAction`."""


@dataclass(frozen=True)
class AddResourceAction(ModifyResourceBaseAction):
    """`AddResourceAction` will add (clone) a resource.

    This action is based on the original optimos implementation,
    see `resolve_add_resources_in_process` in that project.

    It first gets all tasks sorted by the number of task instances,
    that have either a waiting or idle time (descending).
    For each task, it gets the resource_profile for that task, and then:
    - If the profile contains only one resource...
      - ...which in turn has only one task assigned, it will clone that resource.
      - ...which has more than one task assigned, it will instead try to remove the
        least done task from the resource. (Only tasks, that are executed more than once
        by it and are also done by other resources, are considered).
        This should give the resource more time to do the "problem" task.
    - Else if the profile contains more than one resource, iterate over those resources
      sorted by number of times the task is done by the resource (desc).
        - If the resource has only one task assigned, it will clone the resource.
        - If the resource has more than one task assigned, it will try to remove the
          least done (other) task from the resource. (see above)

    """

    @staticmethod
    def rate_self(
        store: Store, input: SelfRatingInput
    ) -> (
        tuple[Literal[RATING.NOT_APPLICABLE], None] | tuple[RATING, "AddResourceAction"]
    ):
        """Generate a best set of parameters & self-evaluates this action."""
        base_evaluation = input.base_evaluation
        tasks = base_evaluation.get_task_names_sorted_by_waiting_time_desc()

        return RATING.NOT_APPLICABLE, None
