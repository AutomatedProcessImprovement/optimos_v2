from dataclasses import dataclass

from dataclass_wizard import JSONWizard

from o2.models.constraints import ConstraintsType
from o2.models.legacy_constraints import GlobalConstraints, WorkMasks
from o2.models.timetable import Resource, TimetableType
from o2.models.evaluation import Evaluation
from o2.store import Store
from o2.models.state import State


@dataclass(frozen=True)
class JSONSolution(JSONWizard):
    """Class to represent a solution in JSON format.

    Similar to the format of legacy optimos, it's used to make o2 compatible with
    the legacy UI.
    """

    solution_info: "_SolutionInfo"
    sim_params: TimetableType
    cons_params: ConstraintsType
    name: str
    iteration: int

    @staticmethod
    def from_evaluation(
        store: Store, state: State, evaluation: Evaluation
    ) -> "JSONSolution":
        pools: dict[str, _ResourceInfo] = {}
        for resource in state.timetable.get_all_resources():
            constraints = store.constraints.get_legacy_constraints_for_resource(
                resource.id
            )
            assert constraints is not None
            calendar = state.timetable.get_calendar_for_resource(resource.id)
            assert calendar is not None
            pools[f"{resource.id}"] = _ResourceInfo(
                total_amount=resource.get_total_cost(state.timetable),
                never_work_masks=constraints.never_work_masks,
                always_work_masks=constraints.always_work_masks,
                shifts=[calendar.to_work_masks()],
                id=resource.id,
                max_weekly_cap=constraints.global_constraints.max_weekly_cap,
                max_daily_cap=constraints.global_constraints.max_daily_cap,
                max_consecutive_cap=constraints.global_constraints.max_consecutive_cap,
                max_shifts_day=constraints.global_constraints.max_shifts_day,
                max_shifts_week=constraints.global_constraints.max_shifts_week,
                is_human=constraints.global_constraints.is_human,
                name=resource.name,
                cost_per_hour=resource.cost_per_hour,
                amount=resource.amount,
                assigned_tasks=resource.assigned_tasks,
                calendar=resource.calendar,
            )
        return JSONSolution(
            sim_params=state.timetable,
            cons_params=store.constraints,
            name="Optimos Run",
            iteration=-1,
            solution_info=_SolutionInfo(
                mean_process_cycle_time=evaluation.avg_cycle_time,
                deviation_info=_DeviationInfo(
                    # TODO
                    cycle_time_deviation=0,
                    execution_duration_deviation=0,
                    dev_type=0,
                ),
                pool_utilization=evaluation.resource_utilizations,
                pool_time=evaluation.resource_worked_times,
                pool_cost={
                    f"{resource.id}": float(cost)
                    for resource, cost in state.timetable.get_resources_with_cost()
                },
                total_pool_cost=evaluation.total_cost,
                total_pool_time=evaluation.total_cycle_time,
                available_time=evaluation.resource_available_times,
                pools_info=_PoolsInfo(
                    task_allocations={
                        f"{resource.id}": resource.assigned_tasks
                        for resource in state.timetable.get_all_resources()
                    },
                    pools=pools,
                ),
            ),
        )


@dataclass(frozen=True)
class _SolutionInfo(JSONWizard):
    pools_info: "_PoolsInfo"
    mean_process_cycle_time: float
    deviation_info: "_DeviationInfo"
    pool_utilization: dict[str, float]
    pool_time: dict[str, float]
    pool_cost: dict[str, float]
    total_pool_cost: float
    total_pool_time: float
    available_time: dict[str, float]


@dataclass(frozen=True)
class _PoolsInfo(JSONWizard):
    pools: dict[str, "_ResourceInfo"]
    task_allocations: dict[str, list[str]]


@dataclass(frozen=True)
class _ResourceInfo(
    GlobalConstraints,
    Resource,
    JSONWizard,
):
    total_amount: int
    never_work_masks: WorkMasks
    always_work_masks: WorkMasks
    shifts: list[WorkMasks]


@dataclass(frozen=True)
class _DeviationInfo(JSONWizard):
    cycle_time_deviation: float
    execution_duration_deviation: float
    dev_type: float
