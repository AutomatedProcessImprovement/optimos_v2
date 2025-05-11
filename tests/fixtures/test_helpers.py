from dataclasses import replace
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Optional

from prosimos.execution_info import TaskEvent, Trace
from prosimos.simulation_stats_calculator import (
    KPIInfo,
    KPIMap,
    LogInfo,
    ResourceKPI,
)

from o2.actions.base_actions.base_action import (
    ActionRatingTuple,
    ActionT,
    RateSelfReturnType,
)
from o2.models.evaluation import Evaluation
from o2.models.solution import Solution
from o2.store import Store
from o2.util.helper import random_string
from tests.fixtures.mock_action import MockAction, MockActionParamsType
from tests.fixtures.timetable_generator import TimetableGenerator

if TYPE_CHECKING:
    from o2.models.state import State


def replace_state(store: Store, **kwargs):
    """Updates the state of the store. (not in place)"""
    new_state = replace(store.solution.state, **kwargs)
    evaluation = new_state.evaluate()
    new_solution = Solution(evaluation=evaluation, state=new_state, actions=[])
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
    state: "State",
    x: int,
    y: int,
    total_waiting_time=0,
    force_uniqueness: bool = True,
):
    kpis = KPIMap()
    kpis.cycle_time = KPIInfo()
    kpis.cycle_time.total = x
    kpis.waiting_time = KPIInfo()
    kpis.waiting_time.total = x

    task_kpi = KPIMap()
    task_kpi.idle_time.total = 0
    task_kpi.processing_time.total = y
    task_kpi.processing_time.count = 1

    resource_kpi = ResourceKPI(
        r_profile="_",
        task_allocated=[],
        available_time=y,
        worked_time=60 * 60,
        utilization=0,
    )

    event = TaskEvent(
        p_case=0,
        task_id=random_string(),
        resource_id=random_string(),
        enabled_at=0,
    )
    event.idle_processing_time = x
    event.enabled_datetime = datetime(2000, 1, 1)
    event.started_datetime = event.enabled_datetime + timedelta(  # type: ignore
        seconds=0
    )  # type: ignore
    event.completed_datetime = event.started_datetime + timedelta(  # type: ignore
        seconds=x
    )  # type: ignore
    trace = Trace(
        p_case=0,
        started_at=datetime(2000, 1, 1),
    )
    trace.event_list = [event]

    log_info = LogInfo(None)  # type: ignore
    log_info.started_at = datetime(2000, 1, 1)
    log_info.ended_at = datetime(2000, 1, 1) + timedelta(seconds=x)
    log_info.trace_list = [trace]

    evaluation = Evaluation.from_run_simulation_result(
        {"_": x},
        {"_": lambda x: y},
        state.timetable.batching_rules_exist,
        (
            kpis,
            {"_": task_kpi},
            {"_": resource_kpi},
            log_info,
        ),  # type: ignore
    )

    if force_uniqueness:
        # Add random string to the state to make it unique
        state = replace(state, bpmn_definition=random_string())
        params = MockActionParamsType(random_string=random_string())
    else:
        params = MockActionParamsType(random_string="STRING")

    return Solution(
        evaluation=evaluation,
        state=state,
        actions=[MockAction(params=params)],
    )


def assert_no_first_valid(store: Store, generator: RateSelfReturnType) -> Optional[ActionRatingTuple]:
    for _, action in generator:
        if action is not None and action.check_if_valid(store):
            raise ValueError("Found valid action")


def first_valid(store: Store, generator: RateSelfReturnType[ActionT]) -> ActionRatingTuple[ActionT]:
    if store.current_evaluation.is_empty:
        raise ValueError("Current evaluation is empty!")
    for rating, action in generator:
        if action is not None and action.check_if_valid(store):
            return rating, action
    raise ValueError("No valid action found")


def generate_ranges(start, max_value, min_length):
    """
    Generate all possible ranges of numbers given a start, max, and a minimum length.

    :param start: The starting number of the range.
    :param max_value: The maximum number (inclusive).
    :param min_length: The minimum length of the range.
    :return: A list of tuples representing the ranges.
    """
    ranges = []

    # Iterate over all possible starting points
    for i in range(start, max_value + 1):
        # Iterate over all possible ending points, ensuring minimum length
        for j in range(i + min_length - 1, max_value + 1):
            ranges.append((i, j))

    return ranges


def count_occurrences(strA: str, strB: str) -> int:
    """
    Count the number of occurrences of strB in strA.

    :param strA: The string to search in.
    :param strB: The string to search for.
    :return: The number of occurrences of strB in strA.
    """
    count = 0
    for i in range(len(strA) - len(strB) + 1):
        if strA[i : i + len(strB)] == strB:
            count += 1
    return count
