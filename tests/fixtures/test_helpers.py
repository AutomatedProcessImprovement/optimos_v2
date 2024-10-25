from dataclasses import replace
from typing import TYPE_CHECKING, Optional

from bpdfr_simulation_engine.simulation_stats_calculator import (
    KPIInfo,
    KPIMap,
    LogInfo,
    ResourceKPI,
)

from o2.actions.base_action import ActionRatingTuple, BaseAction, RateSelfReturnType
from o2.models.evaluation import Evaluation
from o2.models.solution import Solution
from o2.store import Store
from o2.util.helper import random_string
from tests.fixtures.mock_action import MockAction
from tests.fixtures.timetable_generator import TimetableGenerator

if TYPE_CHECKING:
    from o2.models.state import State


def replace_state(store: Store, **kwargs):
    """Updates the state of the store. (not in place)"""
    new_state = replace(store.solution.state, **kwargs)
    evaluation = new_state.evaluate()
    new_solution = Solution(
        evaluation=evaluation, state=new_state, parent_state=None, actions=[]
    )
    return Store(
        solution=new_solution,
        constraints=store.constraints,
    )


def replace_timetable(store: Store, **kwargs):
    """Updates the timetable of the store. (not in place)"""
    new_timetable = replace(store.solution.state.timetable, **kwargs)
    return replace_state(store, timetable=new_timetable)


def replace_constraints(store: Store, **kwargs):
    """Updates the constraints of the store (not in place)"""
    new_constraints = replace(store.constraints, **kwargs)
    return Store(
        solution=store.solution,
        constraints=new_constraints,
    )


def first_calendar_first_period_id(store: Store):
    return store.base_timetable.resource_calendars[0].time_periods[0].id


def create_mock_solution(
    state: "State", total_cycle_time: int, total_cost: int, total_waiting_time=0
):
    kpis = KPIMap()
    kpis.cycle_time = KPIInfo()
    kpis.cycle_time.total = total_cycle_time
    kpis.waiting_time = KPIInfo()
    kpis.waiting_time.total = total_cycle_time

    resource_kpi = ResourceKPI(
        r_profile="",
        task_allocated=[],
        available_time=total_cost,
        worked_time=total_cost,
        utilization=0,
    )

    log_info = LogInfo(None)  # type: ignore

    evaluation = Evaluation.from_run_simulation_result(
        state.timetable.get_hourly_rates(),
        (kpis, {}, {TimetableGenerator.RESOURCE_ID: resource_kpi}, log_info),  # type: ignore
    )
    state = replace(state, bpmn_definition=random_string())
    return Solution(evaluation, state, None, [MockAction()])


def assert_no_first_valid(
    store: Store, generator: RateSelfReturnType
) -> Optional[ActionRatingTuple]:
    for _, action in generator:
        if action is not None and action.check_if_valid(store):
            raise ValueError("Found valid action")


def first_valid(store: Store, generator: RateSelfReturnType) -> ActionRatingTuple:
    for rating, action in generator:
        if action is not None and action.check_if_valid(store):
            return rating, action
    raise ValueError("No valid action found")
