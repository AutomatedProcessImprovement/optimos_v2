# Basic Test Suite to test that the fixture is working correctly
import pytest

from o2.models.evaluation import Evaluation
from o2.models.state import State
from o2.simulation_runner import SimulationRunner


def test_simulation_runner(simple_state: State):
    result = SimulationRunner.run_simulation(
        simple_state,
        show_simulation_errors=True,
    )

    evaluation = Evaluation.from_run_simulation_result(
        simple_state.timetable.get_hourly_rates(),
        simple_state.timetable.get_fixed_cost_fns(),
        simple_state.timetable.batching_rules_exist,
        result,
    )

    # Sanity checks
    assert evaluation.total_duration > 0
    assert evaluation.total_cost > 0
    assert evaluation.total_waiting_time > 0

def test_size_batching_rule(two_tasks_state: State):
    """This is mostly a regression test for a bug in the batching engine."""
    rule = TimetableGenerator.batching_size_rule(
        TimetableGenerator.SECOND_ACTIVITY,
        2,
        1.0,
        comparator=COMPARATOR.GREATER_THEN_OR_EQUAL,
    )
    state = two_tasks_state.replace_timetable(
        batch_processing=[rule],
        total_cases=2,
        arrival_time_distribution=TimetableGenerator.arrival_time_distribution(
            # Event every 5 minutes
            min=5 * 60,
            max=5 * 60,
        ),
    )

    global_kpis, task_kpis, resource_kpis, log_info = SimulationRunner.run_simulation(
        state, show_simulation_errors=True
    )

    case_0 = log_info.trace_list[0]
    case_1 = log_info.trace_list[1]

    assert case_0.event_list[0].task_id == TimetableGenerator.FIRST_ACTIVITY
    assert case_0.event_list[1].task_id == TimetableGenerator.SECOND_ACTIVITY
    assert case_1.event_list[0].task_id == TimetableGenerator.FIRST_ACTIVITY
    assert case_1.event_list[1].task_id == TimetableGenerator.SECOND_ACTIVITY

    # Enabled directly
    assert case_0.event_list[0].enabled_at == 0 * 60
    # Enabled after waiting for the first task to complete
    assert case_0.event_list[1].enabled_at == 60 * 60
    # Enabled after second arrival (5 minutes after the first case)
    assert case_1.event_list[0].enabled_at == 5 * 60
    # Enabled after waiting for the first task (of snd case) to complete
    assert case_1.event_list[1].enabled_at == 120 * 60

    # Completed directly after arrival
    assert case_0.event_list[0].completed_at == 60 * 60
    # Completed after processing the the first task
    assert case_1.event_list[0].completed_at == 2 * 60 * 60
    # Completed after processing waiting for the first task of both cases
    # (2h processing time, because no batching bonus)
    assert case_0.event_list[1].completed_at == 4 * 60 * 60
    assert case_1.event_list[1].completed_at == 4 * 60 * 60


def test_large_wt_batching_rule(two_tasks_state: State):
    """This is mostly a regression test for a bug in the batching engine."""
    rule = TimetableGenerator.large_wt_rule(
        # Start batch after 3 hours
        TimetableGenerator.SECOND_ACTIVITY,
        3 * 60 * 60,
        10,
        1.0,
    )
    state = two_tasks_state.replace_timetable(
        batch_processing=[rule],
        total_cases=2,
        arrival_time_distribution=TimetableGenerator.arrival_time_distribution(
            min=5 * 60, max=5 * 60
        ),
    )
    global_kpis, task_kpis, resource_kpis, log_info = SimulationRunner.run_simulation(
        state, show_simulation_errors=True
    )

    case_0 = log_info.trace_list[0]
    case_1 = log_info.trace_list[1]

    # Enabled directly
    assert case_0.event_list[0].enabled_at == 0 * 60
    # Enabled after waiting for the first task to complete
    assert case_0.event_list[1].enabled_at == 60 * 60
    # Enabled after second arrival
    assert case_1.event_list[0].enabled_at == 5 * 60
    # Enabled after waiting for the first task (of snd case) to complete
    assert case_1.event_list[1].enabled_at == 120 * 60

    # Completed after processing the first task
    assert case_0.event_list[0].completed_at == 60 * 60
    # Completed after processing the second task
    assert case_1.event_list[0].completed_at == 2 * 60 * 60
    # Completed after 3 hours of waiting, which starts after the first task is completed
    # -> 1:00 + 3h + 2*1h processing time = 6:00
    assert case_0.event_list[1].completed_at == 6 * 60 * 60
    assert case_1.event_list[1].completed_at == 6 * 60 * 60


def test_ready_wt_batching_rule(two_tasks_state: State):
    """This is mostly a regression test for a bug in the batching engine."""
    rule = TimetableGenerator.ready_wt_rule(
        TimetableGenerator.SECOND_ACTIVITY,
        5 * 60 * 60,
    )
    state = two_tasks_state.replace_timetable(
        batch_processing=[rule],
        total_cases=3,
        arrival_time_distribution=TimetableGenerator.arrival_time_distribution(
            min=5 * 60, max=5 * 60
        ),
    )
    global_kpis, task_kpis, resource_kpis, log_info = SimulationRunner.run_simulation(
        state, show_simulation_errors=True
    )

    case_0 = log_info.trace_list[0]
    case_1 = log_info.trace_list[1]
    case_2 = log_info.trace_list[2]
    assert case_0.event_list[0].enabled_at == 0 * 60
    assert case_1.event_list[0].enabled_at == 5 * 60
    assert case_0.event_list[1].enabled_at == 1 * 60 * 60
    assert case_1.event_list[1].enabled_at == 2 * 60 * 60
    assert case_2.event_list[1].enabled_at == 3 * 60 * 60

    assert case_0.event_list[0].completed_at == 1 * 60 * 60
    assert case_1.event_list[0].completed_at == 2 * 60 * 60
    # The cases are completed only after 5 hours of waiting after the last enabled event
    # 3:00 + 5h + 3*1h processing = 11:00 completed
    assert case_0.event_list[1].completed_at == 11 * 60 * 60
    assert case_1.event_list[1].completed_at == 11 * 60 * 60
    assert case_2.event_list[1].completed_at == 11 * 60 * 60
