from dataclasses import replace

from bpdfr_simulation_engine.simulation_stats_calculator import KPIInfo, KPIMap

from o2.actions.base_action import BaseAction
from o2.models.evaluation import Evaluation
from o2.models.solution import Solution
from o2.store import Store
from o2.util.helper import random_string
from tests.fixtures.mock_action import MockAction


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


def create_mock_solution(state, total_cycle_time, total_cost, total_waiting_time=0):
    kpis = KPIMap()
    kpis.cycle_time = KPIInfo()
    kpis.cycle_time.total = total_cycle_time
    kpis.waiting_time = KPIInfo()
    kpis.waiting_time.total = total_cycle_time
    cost_kpi = KPIMap()
    cost_kpi.cost.total = total_cost

    evaluation = Evaluation(kpis, {"_": cost_kpi}, {}, None)  # type: ignore
    state = replace(state, bpmn_definition=random_string())
    return Solution(evaluation, state, None, [MockAction()])
