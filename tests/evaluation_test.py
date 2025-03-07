from datetime import datetime, timezone

from o2.models.days import DAY
from o2.models.state import State
from tests.fixtures.timetable_generator import TimetableGenerator


def test_evaluation_calculation_without_batching(one_task_state: State):
    """
    Test the evaluation calculation without batching & waiting times
    """
    state = one_task_state.replace_timetable(
        # Resource has cost of $10/h
        resource_profiles=TimetableGenerator.resource_pools([TimetableGenerator.FIRST_ACTIVITY], 10),
        # Working one case takes 30min
        task_resource_distribution=TimetableGenerator.task_resource_distribution_simple(
            [TimetableGenerator.FIRST_ACTIVITY], 30 * 60
        ),
        # Work from 9 to 17 (8h)
        resource_calendars=TimetableGenerator.resource_calendars(9, 18, include_end_hour=False),
        # One Case every 45min
        arrival_time_distribution=TimetableGenerator.arrival_time_distribution(45 * 60, 45 * 60),
        # Cases from 9:00 to 17:59 (~8h)
        arrival_time_calendar=TimetableGenerator.arrival_time_calendar(9, 17, include_end_hour=True),
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
    assert evaluation.total_cycle_time == 49.25 * 60 * 60
    # No waiting time, so the total time is the same as the processing time
    assert evaluation.avg_cycle_time_by_case == 30 * 60
    # Total cycle time is the same as the total time
    assert evaluation.total_duration == 26 * 30 * 60
    assert evaluation.avg_waiting_time_by_case == 0

    assert evaluation.avg_idle_wt_per_task_instance == 0
    assert evaluation.avg_batch_processing_time_per_task_instance == 30 * 60

    # The first cases of each day don't have any waiting time (3 cases)
    # So we have 23 cases with 15min waiting time
    # (45min arrival time - 30min processing time)
    # Also for the first two days we have 15min idle time at the end of the day
    assert evaluation.total_resource_idle_time == (23 * 15 + 2 * 15) * 60

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
    assert evaluation.resource_utilizations[TimetableGenerator.RESOURCE_ID] == (26 * 0.5) / (9 * 2 + 1.25)


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
        task_resource_distribution=TimetableGenerator.task_resource_distribution_simple(
            [TimetableGenerator.FIRST_ACTIVITY], 30 * 60
        ),
        # Work from 9 to 17 (8h)
        resource_calendars=TimetableGenerator.resource_calendars(9, 18, include_end_hour=False),
        # One Case every 45min
        arrival_time_distribution=TimetableGenerator.arrival_time_distribution(45 * 60, 45 * 60),
        # Cases from 9:00 to 17:59 (~8h)
        arrival_time_calendar=TimetableGenerator.arrival_time_calendar(9, 17, include_end_hour=True),
        total_cases=26,
    )

    evaluation = state.evaluate()

    assert evaluation.total_fixed_cost == 26 * 15
    # 9h * 2 days, 1.25h (0min WT + 30min PT + 15min WT + 30min PT) = 19.25h
    assert evaluation.total_cost_for_worked_time == 19.25 * 10

    assert evaluation.total_cost == 26 * 15 + 19.25 * 10
    assert evaluation.get_total_cost_per_task()[TimetableGenerator.FIRST_ACTIVITY] == 26 * 15 + 26 * 0.5 * 10
    assert evaluation.get_avg_cost_per_task()[TimetableGenerator.FIRST_ACTIVITY] == 0.5 * 10 + 15


def test_evaluation_with_intra_task_idling(one_task_state: State):
    state = one_task_state.replace_timetable(
        # Resource has cost of $10/h
        resource_profiles=TimetableGenerator.resource_pools(
            [TimetableGenerator.FIRST_ACTIVITY], 10, fixed_cost_fn="15"
        ),
        # Working one case takes 4h
        task_resource_distribution=TimetableGenerator.task_resource_distribution_simple(
            [TimetableGenerator.FIRST_ACTIVITY], 4 * 60 * 60
        ),
        # Work from 9 to 11:00 (2h)
        resource_calendars=TimetableGenerator.resource_calendars(
            9, 11, include_end_hour=False, only_week_days=True
        ),
        # One Case every 4h
        arrival_time_distribution=TimetableGenerator.arrival_time_distribution(4 * 60 * 60, 4 * 60 * 60),
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
    assert evaluation.task_kpis[TimetableGenerator.FIRST_ACTIVITY].idle_time.total == (7 * 22 + 48) * 60 * 60
    assert evaluation.total_task_idle_time == (7 * 22 + 48) * 60 * 60


def test_evaluation_with_intra_task_idling_task_stats(one_task_state: State):
    state = one_task_state.replace_timetable(
        # Resource has cost of $10/h + $15 fixed cost
        resource_profiles=TimetableGenerator.resource_pools(
            [TimetableGenerator.FIRST_ACTIVITY], 10, fixed_cost_fn="15"
        ),
        # Working one case takes 2h
        task_resource_distribution=TimetableGenerator.task_resource_distribution_simple(
            [TimetableGenerator.FIRST_ACTIVITY], 2 * 60 * 60
        ),
        # Work from 9 to 11:00 (2h)
        resource_calendars=TimetableGenerator.resource_calendars(
            9, 11, include_end_hour=False, only_week_days=True
        ),
        # One Case every 1h
        arrival_time_distribution=TimetableGenerator.arrival_time_distribution(1 * 60 * 60, 1 * 60 * 60),
        # Cases from 10:00 to 11:00 (1h)
        arrival_time_calendar=TimetableGenerator.arrival_time_calendar(
            10, 14, include_end_hour=False, only_week_days=True
        ),
        total_cases=4,
    )

    evaluation = state.evaluate()

    # Because the first task only arrives one hour later, it spans over two days
    # Processing time is 2h
    assert (
        evaluation.get_total_processing_time_per_task()[TimetableGenerator.FIRST_ACTIVITY] == 2 * 4 * 60 * 60
    )
    assert evaluation.total_processing_time == 2 * 4 * 60 * 60

    # Waiting time (due to resource contention) is 0 for the first task
    # + 11:00 -> 10:00 (next day) + 12:00 -> 10:00 (2 days later) +
    # 13:00 -> 10:00 (3 days later) = 0 + 24-1 + 24*2-2 + 24*3-3 = 0 + 23 + 46 + 69
    assert (
        evaluation.get_total_waiting_time_of_task_id(TimetableGenerator.FIRST_ACTIVITY)
        == (0 + 23 + 46 + 69) * 60 * 60
    )
    assert evaluation.total_waiting_time == (0 + 23 + 46 + 69) * 60 * 60

    # Idle time is 22h for each task (11:00 -> 09:00)
    assert evaluation.get_total_idle_time_of_task_id(TimetableGenerator.FIRST_ACTIVITY) == 22 * 4 * 60 * 60
    assert evaluation.total_task_idle_time == 22 * 4 * 60 * 60
    # Duration is processing time + idle time
    assert (
        evaluation.get_total_duration_time_per_task()[TimetableGenerator.FIRST_ACTIVITY]
        == (2 * 4 + 22 * 4) * 60 * 60
    )
    assert evaluation.total_duration == (2 * 4 + 22 * 4) * 60 * 60
    # Cycle time is duration + waiting time (= wt + processing + idle)
    assert (
        evaluation.get_total_cycle_time_of_task_id(TimetableGenerator.FIRST_ACTIVITY)
        == (2 * 4 + 22 * 4 + 0 + 23 + 46 + 69) * 60 * 60
    )
    # For the whole process, we can't just sum up the waiting times, because a task
    # might wait, while other tasks are being processed, which wont increase the total
    # cycle time
    assert evaluation.total_cycle_time == (2 * 4 + 22 * 4) * 60 * 60

    assert evaluation.avg_idle_wt_per_task_instance == ((138 + 22 * 4) * 60 * 60) / 4
    assert evaluation.avg_batch_processing_time_per_task_instance == 2 * 60 * 60


def test_evaluation_with_waiting_times(one_task_state: State):
    state = one_task_state.replace_timetable(
        # Resource has cost of $10/h
        resource_profiles=TimetableGenerator.resource_pools(
            [TimetableGenerator.FIRST_ACTIVITY], 10, fixed_cost_fn="15"
        ),
        # Working one case takes 1h
        task_resource_distribution=TimetableGenerator.task_resource_distribution_simple(
            [TimetableGenerator.FIRST_ACTIVITY], 1 * 60 * 60
        ),
        # Work from 9 to 18 (9h)
        resource_calendars=TimetableGenerator.resource_calendars(
            9, 18, include_end_hour=False, only_week_days=True
        ),
        # One Case every 30min
        arrival_time_distribution=TimetableGenerator.arrival_time_distribution(30 * 60, 30 * 60),
        # Cases from 9:00 to 16:59 (~8h)
        arrival_time_calendar=TimetableGenerator.arrival_time_calendar(
            9, 17, include_end_hour=False, only_week_days=True
        ),
        total_cases=8,
    )

    evaluation = state.evaluate()

    # 0 for the first
    # 30min for the second
    # 1h for the third
    # 1h30min for the fourth
    # ....
    assert evaluation.total_waiting_time == sum(i * 0.5 for i in range(8)) * 60 * 60

    assert evaluation.avg_waiting_time_by_case == (0.5 * (7 / 2)) * 60 * 60
    assert evaluation.avg_idle_wt_per_task_instance == (0.5 * (7 / 2)) * 60 * 60
    # 1 hour processing time + 1.75h wt (on avg) times 8 cases
    assert evaluation.sum_of_cycle_times == 8 * (1 + (0.5 * (7 / 2))) * 60 * 60
    assert evaluation.sum_of_durations == 8 * 60 * 60
    assert evaluation.total_cycle_time == 8 * 60 * 60
    assert evaluation.total_duration == 8 * 60 * 60
    assert evaluation.total_processing_time == 8 * 60 * 60
    assert evaluation.avg_batch_processing_time_per_task_instance == 1 * 60 * 60
    assert evaluation.total_task_idle_time == 0

    assert evaluation.get_average_processing_time_per_task()[TimetableGenerator.FIRST_ACTIVITY] == 1 * 60 * 60
    assert evaluation.avg_batching_waiting_time_per_task.get(TimetableGenerator.FIRST_ACTIVITY, 0) == 0
    assert (
        evaluation.get_avg_waiting_time_of_task_id(TimetableGenerator.FIRST_ACTIVITY)
        == (0.5 * (7 / 2)) * 60 * 60
    )
    assert (
        evaluation.get_avg_duration_time_per_task()[TimetableGenerator.FIRST_ACTIVITY]
        == (1 + (0.5 * (7 / 2))) * 60 * 60
    )
    assert (
        evaluation.get_total_cycle_time_of_task_id(TimetableGenerator.FIRST_ACTIVITY)
        == (8 * (1 + (0.5 * (7 / 2)))) * 60 * 60
    )

    assert evaluation.get_total_duration_time_per_task()[TimetableGenerator.FIRST_ACTIVITY] == 8 * 60 * 60


def test_evaluation_with_wt_and_idle_batching(one_task_state: State):
    state = one_task_state.replace_timetable(
        # Resource has cost of $10/h
        resource_profiles=TimetableGenerator.resource_pools(
            [TimetableGenerator.FIRST_ACTIVITY], 10, fixed_cost_fn="15"
        ),
        # Working one case takes 1h
        task_resource_distribution=TimetableGenerator.task_resource_distribution_simple(
            [TimetableGenerator.FIRST_ACTIVITY], 1 * 60 * 60
        ),
        # Work from 9 to 18 (9h)
        resource_calendars=TimetableGenerator.resource_calendars(
            9, 18, include_end_hour=False, only_week_days=True
        ),
        # One Case every 24h
        arrival_time_distribution=TimetableGenerator.arrival_time_distribution(
            24 * 60 * 60,
            24 * 60 * 60,
        ),
        # Cases from 9:00 to 10:00
        arrival_time_calendar=TimetableGenerator.arrival_time_calendar(
            9, 10, include_end_hour=False, only_week_days=False
        ),
        # Batch Size of 4 (Meaning 4 days are needed to for a single batch)
        # Will work twice as fast, e.g. only needed 2 hours for 4 tasks
        batch_processing=[
            TimetableGenerator.batching_size_rule(
                TimetableGenerator.FIRST_ACTIVITY, 4, duration_distribution=0.5
            )
        ],
        total_cases=8,
    )

    evaluation = state.evaluate()

    # 1st case in batch waits 3*24h, 2nd 2*24h, 3rd 24h, 4th 0h
    assert evaluation.total_waiting_time == (3 * 24 + 2 * 24 + 1 * 24) * 2 * 60 * 60

    assert evaluation.avg_idle_wt_per_task_instance == (((3 * 24 + 2 * 24 + 1 * 24) * 2) / 8) * 60 * 60

    # We got two batches with 2 hours each, divided by 8 task_instances
    assert evaluation.avg_batch_processing_time_per_task_instance == ((2 * 2) / 8) * 60 * 60

    # Due to batching the processing time is increased, but still less than 4 * 1h
    assert evaluation.get_average_processing_time_per_task()[TimetableGenerator.FIRST_ACTIVITY] == 2 * 60 * 60


def test_batch_detection(one_task_state: State):
    state = one_task_state.replace_timetable(
        # Resource has cost of $10/h
        resource_profiles=TimetableGenerator.resource_pools(
            [TimetableGenerator.FIRST_ACTIVITY], 10, fixed_cost_fn="15"
        ),
        # Working one case takes 2h
        task_resource_distribution=TimetableGenerator.task_resource_distribution_simple(
            [TimetableGenerator.FIRST_ACTIVITY], 2 * 60 * 60
        ),
        # Work from 9 to 17 (8h)
        resource_calendars=TimetableGenerator.resource_calendars(
            9,
            17,
            include_end_hour=False,
            only_week_days=True,
        ),
        # One Case every 1h
        arrival_time_distribution=TimetableGenerator.arrival_time_distribution(
            1 * 60 * 60,
            1 * 60 * 60,
        ),
        # Cases from 9:00 to 17:00
        arrival_time_calendar=TimetableGenerator.arrival_time_calendar(
            9,
            17,
            include_end_hour=False,
            only_week_days=False,
        ),
        # Batch Size of 4 (Meaning 4 are needed to for a single batch)
        # All together will then take 1h
        batch_processing=[
            TimetableGenerator.batching_size_rule(
                TimetableGenerator.FIRST_ACTIVITY, 4, duration_distribution=1 / 4
            )
        ],
        total_cases=16,
    )

    evaluation = state.evaluate()

    # sanity checks
    # first day (9:00 -> 17:00 = 8h) + night time (17:00 -> 9:00 = 16h)
    # + another day (9:00 -> 17:00 = 8h) + night time (17:00 -> 9:00 = 16h)
    # + 1h for the last case = 2*8 + 2*16 + 1 = 49h
    assert evaluation.total_cycle_time == 49 * 60 * 60
    # 16 cases * 1.5h avg waiting time (0-3h)
    assert evaluation.total_waiting_time == (16 * 1.5) * 60 * 60
    # 2 * 4 cases idle over night (17:00 -> 9:00 = 16h)
    assert evaluation.total_task_idle_time == (2 * 4 * 16) * 60 * 60
    # The resource is only working 4*2h, but is available for 8h for the first two days
    # and 1h for the last day
    # TODO: This stat ignores the initial 3h of working time, due
    # to it thinking "the process hasn't really started"
    assert evaluation.total_resource_idle_time == ((8 * 2 + 1 - 3) - 4 * 2) * 60 * 60

    assert evaluation.total_processing_time == (16 * 2) * 60 * 60
    assert evaluation.total_task_idle_time == (2 * 4 * 16) * 60 * 60
    assert evaluation.total_duration == (16 * 2 + 2 * 4 * 16) * 60 * 60

    # Check Calculated batches
    # TODO: Fix this test
    # assert evaluation.batches is not None
    # assert len(evaluation.batches) == 4
    # snd_batch_key = list(evaluation.batches.keys())[1]
    # assert snd_batch_key == (
    #     TimetableGenerator.FIRST_ACTIVITY,
    #     TimetableGenerator.RESOURCE_ID,
    #     datetime(2000, 1, 3, 16, 0, tzinfo=timezone.utc),
    # )
    # snd_batch = evaluation.batches[snd_batch_key]
    # assert snd_batch["activity"] == TimetableGenerator.FIRST_ACTIVITY
    # assert snd_batch["resource"] == TimetableGenerator.RESOURCE_ID
    # assert snd_batch["start"] == datetime(2000, 1, 3, 16, 0, tzinfo=timezone.utc)
    # assert snd_batch["size"] == 4
    # # The first case in the batch is the 1st case, so it needs to wait 3h
    # assert snd_batch["wt_first"] == 3 * 60 * 60
    # # The last case in the batch is the 4th case, so it has no waiting time
    # assert snd_batch["wt_last"] == 0
    # # 2h + 16h idle
    # assert snd_batch["real_proc"] == (2 + 16) * 60 * 60
    # # 2h
    # assert snd_batch["ideal_proc"] == 2 * 60 * 60
