from o2.models.state import State
from tests.fixtures.timetable_generator import TimetableGenerator


def test_evaluation_calculation_without_batching(one_task_state: State):
    """
    Test the evaluation calculation without batching & waiting times
    """
    state = one_task_state.replace_timetable(
        # Resource has cost of $10/h
        resource_profiles=TimetableGenerator.resource_pools(
            [TimetableGenerator.FIRST_ACTIVITY], 10
        ),
        # Working one case takes 30min
        task_resource_distribution=TimetableGenerator.simple_task_resource_distribution(
            [TimetableGenerator.FIRST_ACTIVITY], 30 * 60
        ),
        # Work from 9 to 17 (8h)
        resource_calendars=TimetableGenerator.resource_calendars(
            9, 18, include_end_hour=False
        ),
        # One Case every 45min
        arrival_time_distribution=TimetableGenerator.arrival_time_distribution(
            45 * 60, 45 * 60
        ),
        # Cases from 9:00 to 17:59 (~8h)
        arrival_time_calendar=TimetableGenerator.arrival_time_calendar(
            9, 17, include_end_hour=True
        ),
        total_cases=26,
    )

    evaluation = state.evaluate()

    # We only got 9 hours per day, so we are able to do 12 full cases
    # per day (9h / 45min = 12)
    # Meaning our total time must be 26 / 12 = 2 days + 2 cases
    # Because the first case again, just starts at 9:00, we can ignore it
    # But we need to add the time for the last case to be finished (30min)
    # => 2 days + 1 * 45min + 9h = 2d + 0,75h+ 0,5h +9h = 2d + 10,25h
    # (The first day begins at 9:00, so the first day is only 15h long)
    # 15h + 24h + 10,25h = 49,25h
    assert evaluation.total_time == 49.25 * 60 * 60
    # No waiting time, so the total time is the same as the processing time
    assert evaluation.avg_cycle_time_by_case == 30 * 60
    # Total cycle time is the same as the total time
    assert evaluation.total_cycle_time == 26 * 30 * 60
    assert evaluation.avg_waiting_time_by_case == 0

    # The first cases of each day don't have any waiting time (3 cases)
    # So we have 23 cases with 15min waiting time
    # (45min arrival time - 30min processing time)
    # Also for the first two days we have 15min idle time at the end of the day
    assert evaluation.total_idle_time == (23 * 15 + 2 * 15) * 60

    # We have no fixed costs setup
    assert evaluation.total_fixed_cost == 0

    # We have 26 cases, each case takes 30min, so we have 13h of work
    # 13h * $10 = $130. (No waiting time, so we can ignore cost for idle-ing)
    assert evaluation.total_cost_for_available_time == 130
    # # 9h * 2 days, 1.25h (0min WT + 30min PT + 15min WT + 30min PT) = 19.25h
    assert evaluation.total_cost == evaluation.total_cost_for_worked_time == 19.25 * 10

    assert (
        round(evaluation.resource_worked_times[TimetableGenerator.RESOURCE_ID] / 60)
        # 9h * 2 days, 1.25h (0min WT + 30min PT + 15min WT + 30min PT) for the last day
        == (9 * 2 + 1.25) * 60
    )

    assert (
        evaluation.resource_available_times[TimetableGenerator.RESOURCE_ID]
        # 26 cases * 30min
        == 26 * 0.5 * 60 * 60
    )

    # Should be the ratio between worked time and available time
    assert evaluation.resource_utilizations[TimetableGenerator.RESOURCE_ID] == (
        26 * 0.5
    ) / (9 * 2 + 1.25)
