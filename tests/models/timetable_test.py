from o2.models.days import DAY
from o2.models.legacy_constraints import WorkMasks
from o2.models.state import State
from o2.models.timetable import Resource, ResourceCalendar, TimePeriod
from o2.util.helper import name_is_clone_of
from tests.fixtures.timetable_generator import TimetableGenerator


def test_time_period_bitmask():
    time_period = TimePeriod(
        from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="08:00", end_time="16:00"
    )
    expected_bitarray = [
        0,  # 00:00 - 01:00
        0,  # 01:00 - 02:00
        0,  # 02:00 - 03:00
        0,  # 03:00 - 04:00
        0,  # 04:00 - 05:00
        0,  # 05:00 - 06:00
        0,  # 06:00 - 07:00
        0,  # 07:00 - 08:00
        1,  # 08:00 - 09:00
        1,  # 09:00 - 10:00
        1,  # 10:00 - 11:00
        1,  # 11:00 - 12:00
        1,  # 12:00 - 13:00
        1,  # 13:00 - 14:00
        1,  # 14:00 - 15:00
        1,  # 15:00 - 16:00
        0,  # 16:00 - 17:00
        0,  # 17:00 - 18:00
        0,  # 18:00 - 19:00
        0,  # 19:00 - 20:00
        0,  # 20:00 - 21:00
        0,  # 21:00 - 22:00
        0,  # 22:00 - 23:00
        0,  # 23:00 - 24:00
    ]

    expected_bitmask = int("".join(map(str, expected_bitarray)), 2)

    assert time_period.to_bitmask() == expected_bitmask


def test_time_period_bitmask_complex():
    time_period = TimePeriod(
        from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="22:00", end_time="23:59"
    )
    expected_bitarray = [
        0,  # 00:00 - 01:00
        0,  # 01:00 - 02:00
        0,  # 02:00 - 03:00
        0,  # 03:00 - 04:00
        0,  # 04:00 - 05:00
        0,  # 05:00 - 06:00
        0,  # 06:00 - 07:00
        0,  # 07:00 - 08:00
        0,  # 08:00 - 09:00
        0,  # 09:00 - 10:00
        0,  # 10:00 - 11:00
        0,  # 11:00 - 12:00
        0,  # 12:00 - 13:00
        0,  # 13:00 - 14:00
        0,  # 14:00 - 15:00
        0,  # 15:00 - 16:00
        0,  # 16:00 - 17:00
        0,  # 17:00 - 18:00
        0,  # 18:00 - 19:00
        0,  # 19:00 - 20:00
        0,  # 20:00 - 21:00
        0,  # 21:00 - 22:00
        1,  # 22:00 - 23:00
        1,  # 23:00 - 24:00
    ]

    expected_bitmask = int("".join(map(str, expected_bitarray)), 2)

    assert time_period.to_bitmask() == expected_bitmask


def test_time_period_from_bitmask_simple():
    expected_time_period = TimePeriod(
        from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="08:00", end_time="16:00"
    )

    bitarray = [
        0,  # 00:00 - 01:00
        0,  # 01:00 - 02:00
        0,  # 02:00 - 03:00
        0,  # 03:00 - 04:00
        0,  # 04:00 - 05:00
        0,  # 05:00 - 06:00
        0,  # 06:00 - 07:00
        0,  # 07:00 - 08:00
        1,  # 08:00 - 09:00
        1,  # 09:00 - 10:00
        1,  # 10:00 - 11:00
        1,  # 11:00 - 12:00
        1,  # 12:00 - 13:00
        1,  # 13:00 - 14:00
        1,  # 14:00 - 15:00
        1,  # 15:00 - 16:00
        0,  # 16:00 - 17:00
        0,  # 17:00 - 18:00
        0,  # 18:00 - 19:00
        0,  # 19:00 - 20:00
        0,  # 20:00 - 21:00
        0,  # 21:00 - 22:00
        0,  # 22:00 - 23:00
        0,  # 23:00 - 24:00
    ]

    bitmask = int("".join(map(str, bitarray)), 2)

    time_period = TimePeriod.from_bitmask(bitmask, DAY.MONDAY)

    assert time_period == [expected_time_period]


def test_time_period_from_bitmask_complex():
    expected_time_periods = [
        TimePeriod(
            from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="08:00", end_time="12:00"
        ),
        TimePeriod(
            from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="13:00", end_time="16:00"
        ),
        TimePeriod(
            from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="20:00", end_time="23:00"
        ),
    ]

    bitarray = [
        0,  # 00:00 - 01:00
        0,  # 01:00 - 02:00
        0,  # 02:00 - 03:00
        0,  # 03:00 - 04:00
        0,  # 04:00 - 05:00
        0,  # 05:00 - 06:00
        0,  # 06:00 - 07:00
        0,  # 07:00 - 08:00
        1,  # 08:00 - 09:00
        1,  # 09:00 - 10:00
        1,  # 10:00 - 11:00
        1,  # 11:00 - 12:00
        0,  # 12:00 - 13:00
        1,  # 13:00 - 14:00
        1,  # 14:00 - 15:00
        1,  # 15:00 - 16:00
        0,  # 16:00 - 17:00
        0,  # 17:00 - 18:00
        0,  # 18:00 - 19:00
        0,  # 19:00 - 20:00
        1,  # 20:00 - 21:00
        1,  # 21:00 - 22:00
        1,  # 22:00 - 23:00
        0,  # 23:00 - 24:00
    ]

    bitmask = int("".join(map(str, bitarray)), 2)

    time_period = TimePeriod.from_bitmask(bitmask, DAY.MONDAY)

    assert time_period == expected_time_periods


def test_time_period_to_bitmask_last_hour():
    time_period = TimePeriod(
        from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="22:00", end_time="23:59"
    )
    assert time_period.to_bitmask() == 0b0000000000000000000000011


def test_resource_calendar_verify_valid():
    resource_calendar = ResourceCalendar(
        id="1",
        name="Resource Calendar",
        time_periods=[
            TimePeriod(
                from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="08:00", end_time="12:00"
            ),
            TimePeriod(
                from_=DAY.TUESDAY, to=DAY.TUESDAY, begin_time="08:00", end_time="12:00"
            ),
            TimePeriod(
                from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="12:00", end_time="16:00"
            ),
            TimePeriod(
                from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="20:00", end_time="23:00"
            ),
        ],
    )

    assert resource_calendar.is_valid()


def test_resource_calendar_verify_overlap():
    resource_calendar = ResourceCalendar(
        id="1",
        name="Resource Calendar",
        time_periods=[
            TimePeriod(
                from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="08:00", end_time="12:00"
            ),
            TimePeriod(
                from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="11:00", end_time="23:00"
            ),
        ],
    )

    assert not resource_calendar.is_valid()


def test_resource_calendar_verify_end_before_begin():
    resource_calendar = ResourceCalendar(
        id="1",
        name="Resource Calendar",
        time_periods=[
            TimePeriod(
                from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="12:00", end_time="08:00"
            ),
        ],
    )

    assert not resource_calendar.is_valid()


def test_clone_resource_basic(two_tasks_state: State):
    state = two_tasks_state

    timetable = state.timetable.clone_resource(
        TimetableGenerator.RESOURCE_ID, [TimetableGenerator.FIRST_ACTIVITY]
    )
    original, clone = timetable.resource_profiles[1].resource_list

    assert clone.is_clone_of(original)
    assert name_is_clone_of(
        clone.name,
        original.name,
    )


def test_clone_name_with_timetable_suffix(two_tasks_state: State):
    state = two_tasks_state

    timetable = state.timetable.clone_resource(
        TimetableGenerator.RESOURCE_ID, [TimetableGenerator.FIRST_ACTIVITY]
    )
    original, clone = timetable.resource_profiles[1].resource_list

    assert clone.is_clone_of(original)
    assert name_is_clone_of(clone.name, f"{TimetableGenerator.RESOURCE_ID}timetable")


def test_clone_of_clone(two_tasks_state: State):
    state = two_tasks_state

    timetable = state.timetable.clone_resource(
        TimetableGenerator.RESOURCE_ID, [TimetableGenerator.FIRST_ACTIVITY]
    )
    original, clone = timetable.resource_profiles[1].resource_list

    timetable = timetable.clone_resource(clone.id, [TimetableGenerator.FIRST_ACTIVITY])

    clone2 = timetable.resource_profiles[1].resource_list[-1]

    assert clone2 is not None
    assert clone2.id.count("clone") == 1
    assert clone2.is_clone_of(original)
    assert name_is_clone_of(clone2.name, original.id)


def test_clone_resource_timetable(two_tasks_state: State):
    state = two_tasks_state

    timetable = state.timetable.clone_resource(
        TimetableGenerator.RESOURCE_ID, [TimetableGenerator.FIRST_ACTIVITY]
    )
    original, clone = timetable.resource_profiles[1].resource_list

    assert len(timetable.resource_calendars) == 2

    cloned_calendar = timetable.get_calendar_for_resource(clone.id)
    assert cloned_calendar is not None
    assert cloned_calendar.id == f"{clone.id}timetable"

    original_calendar = timetable.get_calendar_for_resource(
        TimetableGenerator.RESOURCE_ID
    )
    assert original_calendar is not None

    assert cloned_calendar.time_periods == original_calendar.time_periods
    assert cloned_calendar.id != original_calendar.id


def test_clone_resource_profiles(two_tasks_state: State):
    state = two_tasks_state

    timetable = state.timetable.clone_resource(
        TimetableGenerator.RESOURCE_ID, [TimetableGenerator.FIRST_ACTIVITY]
    )
    resource_profile = timetable.get_resource_profile(TimetableGenerator.FIRST_ACTIVITY)
    assert resource_profile is not None
    original, clone = resource_profile.resource_list
    assert "_clone_" in clone.id
    assert clone.assigned_tasks == [TimetableGenerator.FIRST_ACTIVITY]

    assert original.cost_per_hour == clone.cost_per_hour
    assert original.amount == clone.amount


def test_clone_distribution(two_tasks_state: State):
    state = two_tasks_state

    timetable = state.timetable.clone_resource(
        TimetableGenerator.RESOURCE_ID, [TimetableGenerator.FIRST_ACTIVITY]
    )
    original, clone = timetable.resource_profiles[1].resource_list

    distribution = timetable.get_task_resource_distribution(
        TimetableGenerator.FIRST_ACTIVITY
    )
    assert distribution is not None
    assert len(distribution.resources) == 2
    assert distribution.resources[0].resource_id == original.id
    assert distribution.resources[1].resource_id == clone.id

    unaffected_distribution = timetable.get_task_resource_distribution(
        TimetableGenerator.SECOND_ACTIVITY
    )

    assert unaffected_distribution is not None
    assert len(unaffected_distribution.resources) == 1
    assert unaffected_distribution.resources[0].resource_id == original.id

    assert timetable.get_task_resource_distribution(
        TimetableGenerator.SECOND_ACTIVITY
    ) == state.timetable.get_task_resource_distribution(
        TimetableGenerator.SECOND_ACTIVITY
    )


def test_remove_resource_calendar(two_tasks_state: State):
    timetable = two_tasks_state.timetable.clone_resource(
        TimetableGenerator.RESOURCE_ID, [TimetableGenerator.FIRST_ACTIVITY]
    )

    timetable = timetable.remove_resource(TimetableGenerator.RESOURCE_ID)

    assert len(timetable.resource_calendars) == 1
    assert timetable.resource_calendars[0].id != TimetableGenerator.RESOURCE_ID
    assert timetable.get_calendar_for_resource(TimetableGenerator.RESOURCE_ID) is None


def test_remove_resource_profiles(two_tasks_state: State):
    timetable = two_tasks_state.timetable.clone_resource(
        TimetableGenerator.RESOURCE_ID, [TimetableGenerator.FIRST_ACTIVITY]
    )

    timetable = timetable.remove_resource(TimetableGenerator.RESOURCE_ID)

    resource_profile = timetable.get_resource_profile(TimetableGenerator.FIRST_ACTIVITY)
    assert resource_profile is not None

    assert len(resource_profile.resource_list) == 1
    assert resource_profile.resource_list[0].id != TimetableGenerator.RESOURCE_ID
    assert timetable.get_resource(TimetableGenerator.RESOURCE_ID) is None


def test_remove_task_distribution(two_tasks_state: State):
    timetable = two_tasks_state.timetable.clone_resource(
        TimetableGenerator.RESOURCE_ID, [TimetableGenerator.FIRST_ACTIVITY]
    )

    timetable = timetable.remove_resource(TimetableGenerator.RESOURCE_ID)

    distribution = timetable.get_task_resource_distribution(
        TimetableGenerator.FIRST_ACTIVITY
    )
    assert distribution is not None
    assert len(distribution.resources) == 1
    assert distribution.resources[0].resource_id != TimetableGenerator.RESOURCE_ID


def test_remove_task_from_resource(two_tasks_state: State):
    timetable = two_tasks_state.timetable.clone_resource(
        TimetableGenerator.RESOURCE_ID,
        [TimetableGenerator.FIRST_ACTIVITY, TimetableGenerator.SECOND_ACTIVITY],
    )

    timetable = timetable.remove_task_from_resource(
        TimetableGenerator.RESOURCE_ID, TimetableGenerator.SECOND_ACTIVITY
    )

    resource_profile = timetable.get_resource_profile(
        TimetableGenerator.SECOND_ACTIVITY
    )
    assert resource_profile is not None
    assert len(resource_profile.resource_list) == 1

    profile = timetable.get_resource_profile(TimetableGenerator.FIRST_ACTIVITY)
    assert profile is not None
    assert len(profile.resource_list) == 2
    resource = profile.resource_list[0]

    assert resource.id == TimetableGenerator.RESOURCE_ID
    assert resource.assigned_tasks == [TimetableGenerator.FIRST_ACTIVITY]


def test_bit_mask_off_by_one():
    expected_time_periods = [
        TimePeriod.model_validate_json(
            '{"from": "MONDAY","to": "MONDAY","beginTime": "12:00:00","endTime": "18:00:00"}',
        )
    ]

    calendar = ResourceCalendar(
        id="1",
        name="Resource Calendar",
        time_periods=expected_time_periods,  # type: ignore
    )
    work_mask = WorkMasks.from_json(
        '{"monday": 16711807,"tuesday": 16711807,"wednesday": 16711807,"thursday": 16711807,"friday": 16711807,"saturday": 16777215,"sunday": 16777215}'
    )

    assert work_mask.has_intersection(calendar)  # type: ignore


def test_time_period_json():
    time_period = TimePeriod(
        from_=DAY.MONDAY,
        to=DAY.MONDAY,
        begin_time="08:00",
        end_time="16:00",
    )

    time_period_json = time_period.model_dump_json()

    assert "from_" not in time_period_json
    assert time_period == TimePeriod.model_validate_json(time_period_json)
