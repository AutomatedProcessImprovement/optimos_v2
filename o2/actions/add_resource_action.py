from dataclasses import dataclass
from typing import Literal, Optional

from o2.actions.base_action import RateSelfReturnType
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
    def rate_self(store: Store, input: SelfRatingInput) -> RateSelfReturnType:
        """Generate a best set of parameters & self-evaluates this action."""
        parent_evaluation = input.parent_evaluation
        timetable = store.solution.state.timetable
        tasks = parent_evaluation.get_tasks_sorted_by_occurrences_of_wt_and_it()
        for task in tasks:
            resource_profile = timetable.get_resource_profile(task)
            if resource_profile is None:
                continue
            if len(resource_profile.resource_list) == 1:
                resource = resource_profile.resource_list[0]
                if len(resource.assigned_tasks) == 0:
                    continue
                if len(resource.assigned_tasks) == 1:
                    yield (
                        AddResourceAction.get_default_rating(store),
                        AddResourceAction(
                            AddResourceActionParamsType(
                                resource_id=resource.id,
                                task_id=task,
                                clone_resource=True,
                            )
                        ),
                    )
                else:
                    least_done_task = AddResourceAction._find_least_done_task_to_remove(
                        store, input, resource.id, task
                    )
                    if least_done_task is not None:
                        yield (
                            AddResourceAction.get_default_rating(store),
                            AddResourceAction(
                                AddResourceActionParamsType(
                                    resource_id=resource.id,
                                    task_id=least_done_task,
                                    remove_task_from_resource=True,
                                )
                            ),
                        )
            else:
                sorted_resources = (
                    parent_evaluation.get_resources_sorted_by_task_execution_count(task)
                )
                for resource_id in sorted_resources:
                    resource = timetable.get_resource(resource_id)
                    if resource is None:
                        continue
                    if len(resource.assigned_tasks) == 0:
                        continue
                    if len(resource.assigned_tasks) == 1:
                        yield (
                            AddResourceAction.get_default_rating(store),
                            AddResourceAction(
                                AddResourceActionParamsType(
                                    resource_id=resource.id,
                                    task_id=task,
                                    clone_resource=True,
                                )
                            ),
                        )
                    else:
                        least_done_task = (
                            AddResourceAction._find_least_done_task_to_remove(
                                store, input, resource.id, task
                            )
                        )
                        if least_done_task is not None:
                            yield (
                                AddResourceAction.get_default_rating(store),
                                AddResourceAction(
                                    AddResourceActionParamsType(
                                        resource_id=resource.id,
                                        task_id=least_done_task,
                                        remove_task_from_resource=True,
                                    )
                                ),
                            )

        return

    @staticmethod
    def _find_least_done_task_to_remove(
        store: Store,
        input: SelfRatingInput,
        resource_id: str,
        protected_task: str,
    ) -> Optional[str]:
        """Find the least done task to remove from the resource.

        Only tasks, that are executed more than once by the resource and
        are also done by other resources, are considered.
        Of course the task must differ from the protected task.
        """
        timetable = store.solution.state.timetable
        evaluation = input.parent_evaluation
        resource = timetable.get_resource(resource_id)

        if resource is None:
            return None

        task_executions = evaluation.get_task_execution_count_by_resource(resource_id)

        task_candidates = [
            (timetable.get_resource_profile(task), task_executions.get(task, 0))
            for task in resource.assigned_tasks
            if task != protected_task and task_executions.get(task, 0) > 1
        ]

        if not task_candidates:
            return None
        least_done_task, _ = min(task_candidates, key=lambda x: x[1])
        if least_done_task is None:
            return None
        return least_done_task.id
