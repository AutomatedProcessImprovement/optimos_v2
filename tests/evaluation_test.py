from o2.models.days import DAY
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
    assert evaluation.total_duration == 49.25 * 60 * 60
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
    # 9h * 2 days, 1.25h (0min WT + 30min PT + 15min WT + 30min PT) = 19.25h
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


def test_evaluation_without_batching_but_fixed_costs(one_task_state: State):
    """
    Test the evaluation calculation without batching & waiting times, but with fixed costs
    """
    state = one_task_state.replace_timetable(
        # Resource has cost of $10/h
        resource_profiles=TimetableGenerator.resource_pools(
            [TimetableGenerator.FIRST_ACTIVITY], 10, fixed_cost_fn="15"
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

    assert evaluation.total_fixed_cost == 26 * 15
    # 9h * 2 days, 1.25h (0min WT + 30min PT + 15min WT + 30min PT) = 19.25h
    assert evaluation.total_cost_for_worked_time == 19.25 * 10

    assert evaluation.total_cost == 26 * 15 + 19.25 * 10
    assert (
        evaluation.get_total_cost_per_task()[TimetableGenerator.FIRST_ACTIVITY]
        == 26 * 15 + 26 * 0.5 * 10
    )
    assert (
        evaluation.get_avg_cost_per_task()[TimetableGenerator.FIRST_ACTIVITY]
        == 0.5 * 10 + 15
    )


def test_evaluation_with_intra_task_idling(one_task_state: State):
    state = one_task_state.replace_timetable(
        # Resource has cost of $10/h
        resource_profiles=TimetableGenerator.resource_pools(
            [TimetableGenerator.FIRST_ACTIVITY], 10, fixed_cost_fn="15"
        ),
        # Working one case takes 4h
        task_resource_distribution=TimetableGenerator.simple_task_resource_distribution(
            [TimetableGenerator.FIRST_ACTIVITY], 4 * 60 * 60
        ),
        # Work from 9 to 11:00 (2h)
        resource_calendars=TimetableGenerator.resource_calendars(
            9, 11, include_end_hour=False, only_week_days=True
        ),
        # One Case every 4h
        arrival_time_distribution=TimetableGenerator.arrival_time_distribution(
            4 * 60 * 60, 4 * 60 * 60
        ),
        # Cases from 9:00 to 10:59 (~2h)
        arrival_time_calendar=TimetableGenerator.arrival_time_calendar(
            9, 11, include_end_hour=False, only_week_days=True
        ),
        total_cases=4,
    )

    evaluation = state.evaluate()

    # Each 2 days we finish one case, so we need 4 * 2 = 8 days
    # We have 8 + 2 days weekend, so 10 days, minus 9 hours of the first day
    # and 13 hours of the last day
    assert evaluation.total_duration == (10 * 24 - 9 - 13) * 60 * 60

    # We work all the time, so the utilization is 100%
    assert evaluation.resource_utilizations[TimetableGenerator.RESOURCE_ID] == 1

    # We have 7 "nights" of idling time (11:00 - 9:00, 22h)
    # Additionally we have 48h of weekend idling time
    assert (
        evaluation.task_kpis[TimetableGenerator.FIRST_ACTIVITY].idle_time.total
        == (7 * 22 + 48) * 60 * 60
    )
    assert evaluation.global_kpis.idle_time.total == (7 * 22 + 48) * 60 * 60


def test_evaluation_with_intra_task_idling_task_stats(one_task_state: State):
    state = one_task_state.replace_timetable(
        # Resource has cost of $10/h
        resource_profiles=TimetableGenerator.resource_pools(
            [TimetableGenerator.FIRST_ACTIVITY], 10, fixed_cost_fn="15"
        ),
        # Working one case takes 2h
        task_resource_distribution=TimetableGenerator.simple_task_resource_distribution(
            [TimetableGenerator.FIRST_ACTIVITY], 2 * 60 * 60
        ),
        # Work from 9 to 11:00 (2h)
        resource_calendars=TimetableGenerator.resource_calendars(
            9, 11, include_end_hour=False, only_week_days=True
        ),
        # One Case every 1h
        arrival_time_distribution=TimetableGenerator.arrival_time_distribution(
            1 * 60 * 60, 1 * 60 * 60
        ),
        # Cases from 10:00 to 11:00 (1h)
        arrival_time_calendar=TimetableGenerator.arrival_time_calendar(
            10, 14, include_end_hour=False, only_week_days=True
        ),
        total_cases=4,
    )

    evaluation = state.evaluate()

    # Because the first task only arrives one our later, it spans over two days
    # Processing time is 2h
    assert (
        evaluation.get_total_processing_time_per_task()[
            TimetableGenerator.FIRST_ACTIVITY
        ]
        == 2 * 4 * 60 * 60
    )
    # Waiting time (due to resource contention) is 0 for the first task
    # + 11:00 -> 10:00 (next day) + 12:00 -> 10:00 (2 days later) +
    # 13:00 -> 10:00 (3 days later) = 0 + 24-1 + 24*2-2 + 24*3-3 = 0 + 23 + 46 + 69
    assert (
        evaluation.get_total_waiting_time_of_task_id(TimetableGenerator.FIRST_ACTIVITY)
        == (0 + 23 + 46 + 69) * 60 * 60
    )
    # Idle time is 22h for each task (11:00 -> 09:00)
    assert (
        evaluation.get_total_idle_time_of_task_id(TimetableGenerator.FIRST_ACTIVITY)
        == 22 * 4 * 60 * 60
    )
    # Duration is processing time + idle time
    assert (
        evaluation.get_total_duration_time_per_task()[TimetableGenerator.FIRST_ACTIVITY]
        == (2 * 4 + 22 * 4) * 60 * 60
    )
    # Cycle time is duration + waiting time (= wt + processing + idle)
    assert (
        evaluation.get_total_cycle_time_of_task_id(TimetableGenerator.FIRST_ACTIVITY)
        == (2 * 4 + 22 * 4) * 60 * 60 + (0 + 23 + 46 + 69) * 60 * 60
    )


def test_evaluation_with_waiting_times(one_task_state: State):
    state = one_task_state.replace_timetable(
        # Resource has cost of $10/h
        resource_profiles=TimetableGenerator.resource_pools(
            [TimetableGenerator.FIRST_ACTIVITY], 10, fixed_cost_fn="15"
        ),
        # Working one case takes 1h
        task_resource_distribution=TimetableGenerator.simple_task_resource_distribution(
            [TimetableGenerator.FIRST_ACTIVITY], 1 * 60 * 60
        ),
        # Work from 9 to 18 (9h)
        resource_calendars=TimetableGenerator.resource_calendars(
            9, 18, include_end_hour=False, only_week_days=True
        ),
        # One Case every 30min
        arrival_time_distribution=TimetableGenerator.arrival_time_distribution(
            30 * 60, 30 * 60
        ),
        # Cases from 9:00 to 16:59 (~8h)
        arrival_time_calendar=TimetableGenerator.arrival_time_calendar(
            9, 17, include_end_hour=False, only_week_days=True
        ),
        total_cases=8,
    )

    print(state.timetable.to_json())

    evaluation = state.evaluate()

    # 0 for the first
    # 30min for the second
    # 1h for the third
    # 1h30min for the fourth
    # ....
    assert evaluation.total_waiting_time == sum(i * 0.5 for i in range(8)) * 60 * 60

    assert evaluation.avg_waiting_time_by_case == (0.5 * (7 / 2)) * 60 * 60
    # 1 hour processing time + 1.75h wt (on avg) times 8 cases
    assert evaluation.total_cycle_time == 8 * (1 + (0.5 * (7 / 2))) * 60 * 60
    assert evaluation.total_duration == 8 * 60 * 60
