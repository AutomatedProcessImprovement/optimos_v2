from dataclasses import dataclass
from typing import Optional

from dataclass_wizard import JSONWizard

from o2.actions.base_action import BaseAction
from o2.actions.modify_calendar_base_action import ModifyCalendarBaseAction
from o2.actions.modify_resource_base_action import ModifyResourceBaseAction
from o2.models.constraints import ConstraintsType
from o2.models.evaluation import Evaluation
from o2.models.legacy_constraints import GlobalConstraints, WorkMasks
from o2.models.state import State
from o2.models.timetable import Resource, TimetableType
from o2.pareto_front import ParetoFront
from o2.store import Store
from o2.util.helper import CLONE_REGEX


@dataclass(frozen=True)
class JSONReport(JSONWizard):
    """Class to represent report in JSON format."""

    name: str

    constraints: ConstraintsType
    bpmn_definition: str

    base_solution: "_JSONSolution"
    pareto_fronts: list["_JSONParetoFront"]

    is_final: bool

    approach: Optional[str] = None

    @staticmethod
    def from_store(store: Store, is_final: bool = False) -> "JSONReport":
        return JSONReport(
            name=store.name,
            constraints=store.constraints,
            bpmn_definition=store.state.bpmn_definition,
            base_solution=_JSONSolution.from_state_evaluation(
                store.base_state, store.base_evaluation, store
            ),
            pareto_fronts=[
                _JSONParetoFront.from_pareto_front(pareto_front, store)
                for pareto_front in store.pareto_fronts
            ],
            is_final=is_final,
            approach=str(store.settings.legacy_approach),
        )


@dataclass(frozen=True)
class _JSONParetoFront(JSONWizard):
    solutions: list["_JSONSolution"]

    @staticmethod
    def from_pareto_front(
        pareto_front: "ParetoFront", store: Store
    ) -> "_JSONParetoFront":
        return _JSONParetoFront(
            solutions=[
                _JSONSolution.from_state_evaluation(state, evaluation, store)
                for state, evaluation in zip(
                    pareto_front.states, pareto_front.evaluations
                )
            ]
        )


@dataclass
class _JSONResourceModifiers(JSONWizard):
    deleted: Optional[bool]
    added: Optional[bool]
    shifts_modified: Optional[bool]
    tasks_modified: Optional[bool]


@dataclass(frozen=True)
class _JSONResourceInfo(JSONWizard):
    id: str
    name: str

    worked_time: float
    available_time: float
    utilization: float
    cost_per_week: float
    total_cost: float
    hourly_rate: float
    is_human: bool
    max_weekly_capacity: float
    max_daily_capacity: float
    max_consecutive_capacity: float
    # Timetable
    timetable_bitmask: WorkMasks
    original_timetable_bitmask: WorkMasks
    work_hours_per_week: int
    never_work_bitmask: WorkMasks
    always_work_bitmask: WorkMasks
    # Tasks
    assigned_tasks: list[str]
    added_tasks: list[str]
    removed_tasks: list[str]

    modifiers: "_JSONResourceModifiers"

    @staticmethod
    def from_resource(
        resource: Resource,
        state: State,
        evaluation: Evaluation,
        store: Store,
    ) -> "_JSONResourceInfo":
        timetable = state.timetable.get_calendar_for_resource(
            resource.id
        ) or store.base_state.timetable.get_calendar_for_base_resource(resource.id)
        resource_constraints = store.constraints.get_legacy_constraints_for_resource(
            resource.id
        )
        if state.is_base_state:
            original_time_table = timetable
        else:
            original_time_table = (
                store.base_state.timetable.get_calendar_for_base_resource(resource.id)
            )

        assert timetable is not None
        assert resource_constraints is not None
        assert original_time_table is not None

        relevant_actions = [
            action
            for action in state.actions
            if (
                isinstance(action, ModifyResourceBaseAction)
                and action.params["resource_id"] == resource.id
            )
            or (
                isinstance(action, ModifyCalendarBaseAction)
                and action.params["calendar_id"] == timetable.id
            )
        ]

        deleted = any(
            isinstance(action, ModifyResourceBaseAction)
            and action.params.get("remove_resource")
            for action in relevant_actions
        )

        added = CLONE_REGEX.match(resource.id) is not None

        shifts_modified = any(
            isinstance(action, ModifyCalendarBaseAction) for action in relevant_actions
        )

        tasks_modified = any(
            isinstance(action, ModifyResourceBaseAction)
            and action.params.get("remove_task_from_resource")
            for action in relevant_actions
        )

        original_tasks = store.base_state.timetable.get_tasks(resource.id)
        removed_tasks = [
            task_id
            for task_id in original_tasks
            if task_id not in resource.assigned_tasks
        ]
        added_tasks = [
            task_id
            for task_id in resource.assigned_tasks
            if task_id not in original_tasks
        ]

        return _JSONResourceInfo(
            id=resource.id,
            name=resource.name,
            worked_time=evaluation.resource_worked_times.get(resource.id, 0),
            work_hours_per_week=timetable.total_hours,
            available_time=evaluation.resource_available_times.get(resource.id, 0),
            utilization=evaluation.resource_utilizations.get(resource.id, 0),
            cost_per_week=timetable.total_hours * resource.cost_per_hour,
            total_cost=(evaluation.resource_worked_times.get(resource.id, 0) / 60)
            * resource.cost_per_hour,
            hourly_rate=resource.cost_per_hour,
            is_human=resource_constraints.global_constraints.is_human,
            max_weekly_capacity=resource_constraints.global_constraints.max_weekly_cap,
            max_daily_capacity=resource_constraints.global_constraints.max_daily_cap,
            max_consecutive_capacity=resource_constraints.global_constraints.max_consecutive_cap,
            original_timetable_bitmask=original_time_table.to_work_masks(),
            timetable_bitmask=timetable.to_work_masks(),
            never_work_bitmask=resource_constraints.never_work_masks,
            always_work_bitmask=resource_constraints.always_work_masks,
            assigned_tasks=resource.assigned_tasks,
            modifiers=_JSONResourceModifiers(
                deleted=deleted,
                added=added,
                shifts_modified=shifts_modified,
                tasks_modified=tasks_modified,
            ),
            added_tasks=added_tasks,
            removed_tasks=removed_tasks,
        )


@dataclass(frozen=True)
class _JSONGlobalInfo(JSONWizard):
    average_cost: float
    average_time: float
    average_resource_utilization: float
    total_cost: float


@dataclass(frozen=True)
class _JSONSolution(JSONWizard):
    is_base_solution: bool
    solution_no: int
    global_info: "_JSONGlobalInfo"
    resource_info: dict[str, "_JSONResourceInfo"]
    deleted_resources_info: dict[str, "_JSONResourceInfo"]
    timetable: TimetableType

    actions: list[BaseAction]

    @staticmethod
    def from_state_evaluation(
        state: State, evaluation: Evaluation, store: Store
    ) -> "_JSONSolution":
        return _JSONSolution(
            timetable=state.timetable,
            is_base_solution=state.is_base_state,
            solution_no=1,  # TODO
            global_info=_JSONGlobalInfo(
                average_cost=evaluation.avg_cost,
                average_time=evaluation.avg_cycle_time,
                average_resource_utilization=evaluation.avg_resource_utilization,
                total_cost=evaluation.total_cost,
            ),
            resource_info={
                resource.id: _JSONResourceInfo.from_resource(
                    resource, state, evaluation, store
                )
                for resource in state.timetable.get_all_resources()
            },
            deleted_resources_info={
                resource.id: _JSONResourceInfo.from_resource(
                    resource, state, evaluation, store
                )
                for resource in state.timetable.get_deleted_resources(store.base_state)
            },
            actions=state.actions,
        )