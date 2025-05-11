from collections import Counter
from dataclasses import replace

from o2.models.days import DAY
from o2.models.legacy_constraints import WorkMasks
from o2.models.rule_selector import RuleSelector
from o2.models.settings import Settings
from o2.models.state import State
from o2.models.timetable import (
    COMPARATOR,
    RULE_TYPE,
    BatchingRule,
    FiringRule,
    ResourceCalendar,
    TimePeriod,
    TimetableType,
)
from o2.util.bit_mask_helper import (
    bitmask_to_string,
    find_mixed_ranges_in_bitmask,
    find_most_frequent_overlap,
    string_to_bitmask,
)
from o2.util.helper import name_is_clone_of
from tests.fixtures.test_helpers import (
    count_occurrences,
    generate_ranges,
)
from tests.fixtures.timetable_generator import TimetableGenerator


def test_time_period_bitmask():
    time_period = TimePeriod(from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="08:00", end_time="16:00")
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
    time_period = TimePeriod(from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="22:00", end_time="23:59")
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
    expected_time_period = TimePeriod(from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="08:00", end_time="16:00")

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
        TimePeriod(from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="08:00", end_time="12:00"),
        TimePeriod(from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="13:00", end_time="16:00"),
        TimePeriod(from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="20:00", end_time="23:00"),
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
    time_period = TimePeriod(from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="22:00", end_time="23:59")
    assert time_period.to_bitmask() == 0b0000000000000000000000011


def test_resource_calendar_verify_valid():
    resource_calendar = ResourceCalendar(
        id="1",
        name="Resource Calendar",
        time_periods=[
            TimePeriod(from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="08:00", end_time="12:00"),
            TimePeriod(from_=DAY.TUESDAY, to=DAY.TUESDAY, begin_time="08:00", end_time="12:00"),
            TimePeriod(from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="12:00", end_time="16:00"),
            TimePeriod(from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="20:00", end_time="23:00"),
        ],
    )

    assert resource_calendar.is_valid()


def test_resource_calendar_verify_overlap():
    resource_calendar = ResourceCalendar(
        id="1",
        name="Resource Calendar",
        time_periods=[
            TimePeriod(from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="08:00", end_time="12:00"),
            TimePeriod(from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="11:00", end_time="23:00"),
        ],
    )

    assert not resource_calendar.is_valid()


def test_resource_calendar_verify_end_before_begin():
    resource_calendar = ResourceCalendar(
        id="1",
        name="Resource Calendar",
        time_periods=[
            TimePeriod(from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="12:00", end_time="08:00"),
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

    original_calendar = timetable.get_calendar_for_resource(TimetableGenerator.RESOURCE_ID)
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

    distribution = timetable.get_task_resource_distribution(TimetableGenerator.FIRST_ACTIVITY)
    assert distribution is not None
    assert len(distribution.resources) == 2
    assert distribution.resources[0].resource_id == original.id
    assert distribution.resources[1].resource_id == clone.id

    unaffected_distribution = timetable.get_task_resource_distribution(TimetableGenerator.SECOND_ACTIVITY)

    assert unaffected_distribution is not None
    assert len(unaffected_distribution.resources) == 1
    assert unaffected_distribution.resources[0].resource_id == original.id

    assert timetable.get_task_resource_distribution(
        TimetableGenerator.SECOND_ACTIVITY
    ) == state.timetable.get_task_resource_distribution(TimetableGenerator.SECOND_ACTIVITY)


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

    distribution = timetable.get_task_resource_distribution(TimetableGenerator.FIRST_ACTIVITY)
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

    resource_profile = timetable.get_resource_profile(TimetableGenerator.SECOND_ACTIVITY)
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


def test_work_masks():
    all_day_work_mask = WorkMasks().set_hour_range_for_every_day(0, 24)
    assert bitmask_to_string(all_day_work_mask.get(DAY.MONDAY)) == "1" * 24
    assert bitmask_to_string(all_day_work_mask.get(DAY.SUNDAY)) == "1" * 24

    work_mask = WorkMasks().set_hour_range_for_day(DAY.MONDAY, 10, 12)
    assert bitmask_to_string(work_mask.get(DAY.MONDAY)) == "0" * 10 + "1" * 2 + "0" * 12
    assert bitmask_to_string(work_mask.get(DAY.SUNDAY)) == "0" * 24


def test_work_masks_has_hour_for_day():
    work_mask = WorkMasks().set_hour_range_for_day(DAY.MONDAY, 10, 14)

    assert work_mask.has_hour_for_day(DAY.MONDAY, 10) is True
    assert work_mask.has_hour_for_day(DAY.MONDAY, 11) is True
    assert work_mask.has_hour_for_day(DAY.MONDAY, 12) is True
    assert work_mask.has_hour_for_day(DAY.MONDAY, 13) is True

    assert work_mask.has_hour_for_day(DAY.MONDAY, 9) is False
    assert work_mask.has_hour_for_day(DAY.MONDAY, 14) is False

    assert work_mask.has_hour_for_day(DAY.TUESDAY, 10) is False
    assert work_mask.has_hour_for_day(DAY.SUNDAY, 12) is False


def test_work_masks_is_super_set():
    work_mask = WorkMasks().set_hour_range_for_day(DAY.MONDAY, 8, 17)

    # Calendar is a subset of work_mask
    calendar_subset = ResourceCalendar(
        id="1",
        name="Resource Calendar",
        time_periods=[
            TimePeriod.from_start_end(10, 12, DAY.MONDAY),
            TimePeriod.from_start_end(14, 16, DAY.MONDAY),
        ],
    )
    assert work_mask.is_super_set(calendar_subset) is True

    # Calendar has hours outside work_mask
    calendar_not_subset = ResourceCalendar(
        id="2",
        name="Resource Calendar",
        time_periods=[
            TimePeriod.from_start_end(7, 9, DAY.MONDAY),
            TimePeriod.from_start_end(14, 16, DAY.MONDAY),
        ],
    )
    assert work_mask.is_super_set(calendar_not_subset) is False

    # Calendar has hours on different day
    calendar_different_day = ResourceCalendar(
        id="3",
        name="Resource Calendar",
        time_periods=[
            TimePeriod.from_start_end(10, 12, DAY.MONDAY),
            TimePeriod.from_start_end(14, 16, DAY.TUESDAY),
        ],
    )
    assert work_mask.is_super_set(calendar_different_day) is False


def test_work_masks_set_hour_for_day():
    work_mask = WorkMasks()

    # Set a single hour for Monday
    updated_mask = work_mask.set_hour_for_day(DAY.MONDAY, 10)
    assert bitmask_to_string(updated_mask.get(DAY.MONDAY)) == "0" * 10 + "1" + "0" * 13
    assert bitmask_to_string(updated_mask.get(DAY.TUESDAY)) == "0" * 24

    # Set another hour for Monday
    updated_mask = updated_mask.set_hour_for_day(DAY.MONDAY, 15)
    assert bitmask_to_string(updated_mask.get(DAY.MONDAY)) == "0" * 10 + "1" + "0" * 4 + "1" + "0" * 8

    # Set an hour for a different day
    updated_mask = updated_mask.set_hour_for_day(DAY.FRIDAY, 8)
    assert bitmask_to_string(updated_mask.get(DAY.FRIDAY)) == "0" * 8 + "1" + "0" * 15
    assert bitmask_to_string(updated_mask.get(DAY.MONDAY)) == "0" * 10 + "1" + "0" * 4 + "1" + "0" * 8


def test_work_masks_set_hour_for_every_day():
    work_mask = WorkMasks()

    # Set a single hour for all days
    updated_mask = work_mask.set_hour_for_every_day(12)

    # Check that the hour is set for all days
    for day in DAY:
        assert bitmask_to_string(updated_mask.get(day)) == "0" * 12 + "1" + "0" * 11

    # Set another hour for all days
    updated_mask = updated_mask.set_hour_for_every_day(18)

    # Check that both hours are set for all days
    for day in DAY:
        assert bitmask_to_string(updated_mask.get(day)) == "0" * 12 + "1" + "0" * 5 + "1" + "0" * 5


def test_work_masks_all_day():
    work_mask = WorkMasks.all_day()

    # Check that all hours are set for all days
    for day in DAY:
        assert bitmask_to_string(work_mask.get(day)) == "1" * 24

    # Check has_hour_for_day for a few sample hours
    assert work_mask.has_hour_for_day(DAY.MONDAY, 0) is True
    assert work_mask.has_hour_for_day(DAY.WEDNESDAY, 12) is True
    assert work_mask.has_hour_for_day(DAY.SUNDAY, 23) is True


def test_calendar_work_masks():
    calendar = ResourceCalendar(
        id="1",
        name="Resource Calendar",
        time_periods=[TimePeriod.from_start_end(10, 12, DAY.MONDAY)],
    )
    work_masks = calendar.work_masks
    assert bitmask_to_string(work_masks.get(DAY.MONDAY)) == "0" * 10 + "1" * 2 + "0" * 12


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


def test_bitmasks_by_day():
    calendar = ResourceCalendar(
        id="1",
        name="Resource Calendar",
        time_periods=[
            TimePeriod.from_start_end(12, 15, DAY.TUESDAY),
            TimePeriod(
                from_=DAY.MONDAY,
                to=DAY.TUESDAY,
                begin_time="08:00",
                end_time="12:00",
            ),
        ],
    )

    bitmasks_by_day = calendar.bitmasks_by_day
    assert bitmasks_by_day == [
        (DAY.MONDAY, string_to_bitmask("0" * 7 + "1" * 4 + "0" * 12)),
        (DAY.TUESDAY, string_to_bitmask("0" * 12 + "1" * 3 + "0" * 9)),
        (DAY.TUESDAY, string_to_bitmask("0" * 7 + "1" * 4 + "0" * 12)),
    ]


def test_find_most_frequent_overlap_empty():
    bitmasks = []
    assert find_most_frequent_overlap(bitmasks) is None


def test_find_most_frequent_overlap_adjacent():
    bitmasks = [
        TimePeriod.from_start_end(10, 11).to_bitmask(),
        TimePeriod.from_start_end(11, 12).to_bitmask(),
        TimePeriod.from_start_end(12, 13).to_bitmask(),
    ]
    res = find_most_frequent_overlap(bitmasks)
    assert res is not None
    freq, start, end = res
    assert freq == 1
    assert start == 10
    assert end == 13


def test_find_most_frequent_overlap_simple():
    bitmasks = [
        TimePeriod.from_start_end(10, 13).to_bitmask(),
        TimePeriod.from_start_end(10, 13).to_bitmask(),
        TimePeriod.from_start_end(9, 14).to_bitmask(),
    ]
    res = find_most_frequent_overlap(bitmasks)
    assert res is not None
    freq, start, end = res
    assert freq == 3
    assert start == 10
    assert end == 13


def test_find_most_frequent_overlap_two_equal():
    bitmasks = [
        TimePeriod.from_start_end(10, 13).to_bitmask(),
        TimePeriod.from_start_end(10, 13).to_bitmask(),
        TimePeriod.from_start_end(16, 19).to_bitmask(),
        TimePeriod.from_start_end(16, 19).to_bitmask(),
    ]
    res = find_most_frequent_overlap(bitmasks)
    assert res is not None
    freq, start, end = res
    assert freq == 2
    assert start == 10
    assert end == 13


def test_find_most_frequent_overlap_two_longer():
    bitmasks = [
        TimePeriod.from_start_end(10, 13).to_bitmask(),
        TimePeriod.from_start_end(10, 13).to_bitmask(),
        TimePeriod.from_start_end(16, 20).to_bitmask(),
        TimePeriod.from_start_end(16, 20).to_bitmask(),
    ]
    res = find_most_frequent_overlap(bitmasks)
    assert res is not None
    freq, start, end = res
    assert freq == 2
    assert start == 16
    assert end == 20


def test_find_most_frequent_overlap_min_size():
    bitmasks = [
        TimePeriod.from_start_end(10, 12).to_bitmask(),
        TimePeriod.from_start_end(10, 12).to_bitmask(),
        TimePeriod.from_start_end(10, 12).to_bitmask(),
        TimePeriod.from_start_end(14, 15).to_bitmask(),
        TimePeriod.from_start_end(14, 15).to_bitmask(),
        TimePeriod.from_start_end(14, 15).to_bitmask(),
        TimePeriod.from_start_end(20, 23).to_bitmask(),
        TimePeriod.from_start_end(20, 23).to_bitmask(),
    ]
    res = find_most_frequent_overlap(bitmasks, min_size=2)
    assert res is not None
    freq, start, end = res
    assert freq == 3
    assert start == 10
    assert end == 12


def test_find_most_frequent_overlap_min_sufficient():
    bitmasks = [
        TimePeriod.from_start_end(10, 14).to_bitmask(),
        TimePeriod.from_start_end(11, 15).to_bitmask(),
        TimePeriod.from_start_end(12, 16).to_bitmask(),
    ]
    res = find_most_frequent_overlap(bitmasks, min_size=3)
    assert res is not None
    freq, start, end = res
    assert freq == 1
    assert start == 10
    assert end == 16


def test_get_highest_availability_time_period_no_overlap(multi_resource_state: State):
    calendars = [
        ResourceCalendar(
            id=f"{TimetableGenerator.CALENDAR_ID}_1",
            name=f"{TimetableGenerator.CALENDAR_ID}_1",
            time_periods=[
                TimePeriod.from_start_end(10, 11, DAY.MONDAY),
            ],
        ),
        ResourceCalendar(
            id=f"{TimetableGenerator.CALENDAR_ID}_2",
            name=f"{TimetableGenerator.CALENDAR_ID}_2",
            time_periods=[
                TimePeriod.from_start_end(11, 12, DAY.MONDAY),
            ],
        ),
        ResourceCalendar(
            id=f"{TimetableGenerator.CALENDAR_ID}_3",
            name=f"{TimetableGenerator.CALENDAR_ID}_3",
            time_periods=[
                TimePeriod.from_start_end(12, 13, DAY.MONDAY),
            ],
        ),
    ]
    state = multi_resource_state.replace_timetable(
        resource_calendars=calendars,
    )
    timetable = state.timetable

    assert timetable.get_highest_availability_time_period(
        TimetableGenerator.FIRST_ACTIVITY, 2
    ) == TimePeriod.from_start_end(10, 13, DAY.MONDAY)


def test_get_highest_availability_time_period_overlap(multi_resource_state: State):
    calendars = [
        ResourceCalendar(
            id=f"{TimetableGenerator.CALENDAR_ID}_1",
            name=f"{TimetableGenerator.CALENDAR_ID}_1",
            time_periods=[
                TimePeriod.from_start_end(10, 14, DAY.MONDAY),
            ],
        ),
        ResourceCalendar(
            id=f"{TimetableGenerator.CALENDAR_ID}_2",
            name=f"{TimetableGenerator.CALENDAR_ID}_2",
            time_periods=[
                TimePeriod.from_start_end(11, 15, DAY.MONDAY),
            ],
        ),
        ResourceCalendar(
            id=f"{TimetableGenerator.CALENDAR_ID}_3",
            name=f"{TimetableGenerator.CALENDAR_ID}_3",
            time_periods=[
                TimePeriod.from_start_end(12, 16, DAY.MONDAY),
            ],
        ),
    ]
    state = multi_resource_state.replace_timetable(
        resource_calendars=calendars,
    )
    timetable = state.timetable

    assert timetable.get_highest_availability_time_period(
        TimetableGenerator.FIRST_ACTIVITY, 2
    ) == TimePeriod.from_start_end(12, 14, DAY.MONDAY)


def test_get_highest_availability_time_period_overlap_too_small(
    multi_resource_state: State,
):
    calendars = [
        ResourceCalendar(
            id=f"{TimetableGenerator.CALENDAR_ID}_1",
            name=f"{TimetableGenerator.CALENDAR_ID}_1",
            time_periods=[
                TimePeriod.from_start_end(10, 14, DAY.MONDAY),
            ],
        ),
        ResourceCalendar(
            id=f"{TimetableGenerator.CALENDAR_ID}_2",
            name=f"{TimetableGenerator.CALENDAR_ID}_2",
            time_periods=[
                TimePeriod.from_start_end(11, 15, DAY.MONDAY),
            ],
        ),
        ResourceCalendar(
            id=f"{TimetableGenerator.CALENDAR_ID}_3",
            name=f"{TimetableGenerator.CALENDAR_ID}_3",
            time_periods=[
                TimePeriod.from_start_end(12, 16, DAY.MONDAY),
            ],
        ),
    ]
    state = multi_resource_state.replace_timetable(
        resource_calendars=calendars,
    )
    timetable = state.timetable

    assert timetable.get_highest_availability_time_period(
        TimetableGenerator.FIRST_ACTIVITY, 3
    ) == TimePeriod.from_start_end(10, 16, DAY.MONDAY)


def test_find_mixed_ranges_in_bitmask_simple():
    bit_length = 24
    bitmask = 0b1101011
    start = 0
    max_start = bit_length - 1
    min_length = 3

    expected_ranges = [
        # 1101
        (17, 21),
        # 10101
        (18, 23),
        # 1011
        (20, 24),
    ]

    result = find_mixed_ranges_in_bitmask(bitmask, min_length, start, max_start)

    assert result == expected_ranges


def test_find_mixed_ranges_in_bitmask_complex():
    bit_length = 24
    bitmask = 0b110101110110111
    bitstring = bin(bitmask)[2:].zfill(bit_length)
    start = 9
    max_start = start + 10
    min_length = 3

    all_ranges = generate_ranges(0, len(bitstring), min_length)
    valid_ranges = [
        r
        for r in all_ranges
        if r[0] <= max_start
        and r[0] >= start
        and count_occurrences(bitstring[r[0] : r[1]], "1") == min_length
        # Assure no leading/trailing zeros
        and bitstring[r[0] : r[1]].removeprefix("0").removesuffix("0") == bitstring[r[0] : r[1]]
    ]

    result = find_mixed_ranges_in_bitmask(bitmask, min_length, start, max_start)

    assert Counter(valid_ranges) == Counter(result)


def test_get_time_periods_of_length_excl_idle_simple():
    calendar = ResourceCalendar(
        id=TimetableGenerator.CALENDAR_ID,
        name=TimetableGenerator.CALENDAR_ID,
        time_periods=[
            TimePeriod.from_start_end(10, 12, DAY.MONDAY),
            TimePeriod.from_start_end(13, 14, DAY.MONDAY),
            TimePeriod.from_start_end(15, 17, DAY.MONDAY),
        ],
    )

    assert calendar.get_time_periods_of_length_excl_idle(DAY.MONDAY, 3, 0, 23) == [
        TimePeriod.from_start_end(10, 14, DAY.MONDAY),
        TimePeriod.from_start_end(13, 17, DAY.MONDAY),
        TimePeriod.from_start_end(11, 16, DAY.MONDAY),
    ]

    assert calendar.get_time_periods_of_length_excl_idle(DAY.MONDAY, 3, 0, 12) == [
        TimePeriod.from_start_end(10, 14, DAY.MONDAY),
        TimePeriod.from_start_end(11, 16, DAY.MONDAY),
    ]

    assert calendar.get_time_periods_of_length_excl_idle(DAY.MONDAY, 3, 11, 23) == [
        TimePeriod.from_start_end(13, 17, DAY.MONDAY),
        TimePeriod.from_start_end(11, 16, DAY.MONDAY),
    ]

    assert calendar.get_time_periods_of_length_excl_idle(DAY.MONDAY, 5, 0, 23) == [
        TimePeriod.from_start_end(10, 17, DAY.MONDAY),
    ]

    assert calendar.get_time_periods_of_length_excl_idle(DAY.MONDAY, 6, 0, 23) == []


def test_get_time_periods_of_length_excl_idle_regression():
    calendar = ResourceCalendar(
        id=TimetableGenerator.CALENDAR_ID,
        name=TimetableGenerator.CALENDAR_ID,
        time_periods=[
            TimePeriod.from_start_end(9, 17, DAY.MONDAY),
        ],
    )

    assert calendar.get_time_periods_of_length_excl_idle(DAY.MONDAY, 3, 0, 23) == [
        TimePeriod.from_start_end(9, 12, DAY.MONDAY),
        TimePeriod.from_start_end(13, 16, DAY.MONDAY),
        TimePeriod.from_start_end(11, 14, DAY.MONDAY),
    ]


def test_batching_rule_date_time_merging_simple():
    batching_rule = BatchingRule.from_task_id(
        TimetableGenerator.FIRST_ACTIVITY,
        firing_rules=TimetableGenerator.daily_hour_rule_with_day(
            TimetableGenerator.FIRST_ACTIVITY, DAY.MONDAY, 10, 12
        ).firing_rules[0],
    )

    batching_rule = batching_rule.add_firing_rules(
        TimetableGenerator.daily_hour_rule_with_day(
            TimetableGenerator.FIRST_ACTIVITY, DAY.MONDAY, 12, 14
        ).firing_rules[0]
    )

    assert batching_rule.firing_rules[0] == [
        FiringRule.eq(RULE_TYPE.WEEK_DAY, DAY.MONDAY),
        FiringRule.gte(RULE_TYPE.DAILY_HOUR, 10),
        FiringRule.lt(RULE_TYPE.DAILY_HOUR, 14),
    ]


def test_batching_rule_date_time_merging_complex():
    batching_rule = BatchingRule.from_task_id(
        TimetableGenerator.FIRST_ACTIVITY,
        firing_rules=TimetableGenerator.daily_hour_rule_with_day(
            TimetableGenerator.FIRST_ACTIVITY, DAY.MONDAY, 10, 12
        ).firing_rules[0],
    )

    batching_rule = batching_rule.add_firing_rules(
        TimetableGenerator.daily_hour_rule_with_day(
            TimetableGenerator.FIRST_ACTIVITY, DAY.THURSDAY, 14, 16
        ).firing_rules[0]
    ).add_firing_rules(
        TimetableGenerator.daily_hour_rule(TimetableGenerator.FIRST_ACTIVITY, 12, 14).firing_rules[0]
    )

    assert len(batching_rule.firing_rules) == 2
    assert batching_rule.firing_rules[0][0] == FiringRule(RULE_TYPE.WEEK_DAY, COMPARATOR.EQUAL, DAY.MONDAY)


def test_batching_rule_date_time_merging_with_size():
    batching_rule = BatchingRule.from_task_id(
        TimetableGenerator.FIRST_ACTIVITY,
        firing_rules=[
            FiringRule.eq(RULE_TYPE.WEEK_DAY, DAY.MONDAY),
            FiringRule.gte(RULE_TYPE.DAILY_HOUR, 10),
            FiringRule.lt(RULE_TYPE.DAILY_HOUR, 14),
            FiringRule.gte(RULE_TYPE.SIZE, 2),
        ],
    )

    batching_rule = batching_rule.add_firing_rules(
        TimetableGenerator.daily_hour_rule_with_day(
            TimetableGenerator.FIRST_ACTIVITY, DAY.MONDAY, 16, 18
        ).firing_rules[0]
    )

    assert batching_rule.firing_rules[0] == [
        FiringRule.eq(RULE_TYPE.WEEK_DAY, DAY.MONDAY),
        FiringRule.gte(RULE_TYPE.DAILY_HOUR, 10),
        FiringRule.lt(RULE_TYPE.DAILY_HOUR, 14),
        FiringRule.gte(RULE_TYPE.SIZE, 2),
    ]

    assert batching_rule.firing_rules[1] == [
        FiringRule.eq(RULE_TYPE.WEEK_DAY, DAY.MONDAY),
        FiringRule.gte(RULE_TYPE.DAILY_HOUR, 16),
        FiringRule.lt(RULE_TYPE.DAILY_HOUR, 18),
    ]

    new_batching_rule = batching_rule.add_firing_rules(
        [
            FiringRule.gte(RULE_TYPE.DAILY_HOUR, 10),
            FiringRule.lt(RULE_TYPE.DAILY_HOUR, 18),
        ]
    )
    assert len(new_batching_rule.firing_rules) == 7
    assert new_batching_rule.firing_rules[0] == [
        FiringRule.eq(RULE_TYPE.WEEK_DAY, DAY.MONDAY),
        FiringRule.gte(RULE_TYPE.DAILY_HOUR, 10),
        FiringRule.lt(RULE_TYPE.DAILY_HOUR, 18),
        FiringRule.gte(RULE_TYPE.SIZE, 2),
    ]

    assert new_batching_rule.firing_rules[0][3] == FiringRule.gte(RULE_TYPE.SIZE, 2)

    new_size_batching_rule = new_batching_rule.add_firing_rules(
        [
            FiringRule.eq(RULE_TYPE.WEEK_DAY, DAY.MONDAY),
            FiringRule.gte(RULE_TYPE.DAILY_HOUR, 15),
            FiringRule.lt(RULE_TYPE.DAILY_HOUR, 17),
            FiringRule.gte(RULE_TYPE.SIZE, 10),
        ]
    )
    assert len(new_size_batching_rule.firing_rules) == 7
    assert new_size_batching_rule.firing_rules[0] == [
        FiringRule.eq(RULE_TYPE.WEEK_DAY, DAY.MONDAY),
        FiringRule.gte(RULE_TYPE.DAILY_HOUR, 10),
        FiringRule.lt(RULE_TYPE.DAILY_HOUR, 18),
        FiringRule.gte(RULE_TYPE.SIZE, 10),
    ]

    assert new_size_batching_rule.firing_rules[1] == [
        FiringRule.eq(RULE_TYPE.WEEK_DAY, DAY.TUESDAY),
        FiringRule.gte(RULE_TYPE.DAILY_HOUR, 10),
        FiringRule.lt(RULE_TYPE.DAILY_HOUR, 18),
    ]


def test_equality_of_timetables_simple(one_task_state: State):
    timetable = one_task_state.timetable
    clone = replace(timetable)

    assert timetable == clone
    assert hash(timetable) == hash(clone)

    # Change the clone
    new_resource_clone = clone.clone_resource(
        TimetableGenerator.RESOURCE_ID, [TimetableGenerator.FIRST_ACTIVITY]
    )

    assert timetable != new_resource_clone

    # Remove the added resource
    resource_id = new_resource_clone.resource_profiles[0].resource_list[1].id
    removed_resource_clone = new_resource_clone.remove_resource(resource_id)

    assert timetable == removed_resource_clone


def test_equality_of_timetables_json(batching_state: State):
    timetable = batching_state.timetable
    json_timetable = timetable.to_json()
    clone = TimetableType.from_json(json_timetable)

    assert timetable == clone


def test_equality_of_timetables_batching_rule_change(one_task_state: State):
    Settings.CHECK_FOR_TIMETABLE_EQUALITY = True
    state = one_task_state.replace_timetable(
        batch_processing=[TimetableGenerator.ready_wt_rule(TimetableGenerator.FIRST_ACTIVITY, 5 * 60)],
    )
    timetable = state.timetable
    clone = replace(timetable)

    assert timetable == clone
    assert hash(timetable) == hash(clone)

    # Change the clone
    new_firing_rule = FiringRule.eq(RULE_TYPE.READY_WT, 10 * 60)
    new_batching_rule_clone = clone.add_firing_rule(
        RuleSelector.from_batching_rule(clone.batch_processing[0], (0, 0)),
        new_firing_rule,
    )

    assert timetable != new_batching_rule_clone
    assert hash(timetable) != hash(new_batching_rule_clone)

    # Remove the added firing rule
    batching_rule = new_batching_rule_clone.batch_processing[0]
    batching_rule = batching_rule.remove_firing_rule(RuleSelector.from_batching_rule(batching_rule, (1, 0)))
    assert batching_rule is not None

    restored_clone = new_batching_rule_clone.replace_batching_rule(
        RuleSelector.from_batching_rule(batching_rule, (0, 0)), batching_rule
    )

    assert timetable == restored_clone
    assert hash(timetable) == hash(restored_clone)
    Settings.CHECK_FOR_TIMETABLE_EQUALITY = False


def test_equality_batching_rules():
    Settings.CHECK_FOR_TIMETABLE_EQUALITY = True
    firing_rules = [
        FiringRule.eq(RULE_TYPE.WEEK_DAY, DAY.MONDAY),
        FiringRule.gte(RULE_TYPE.DAILY_HOUR, 10),
        FiringRule.lt(RULE_TYPE.DAILY_HOUR, 12),
    ]
    batching_rule = BatchingRule.from_task_id(
        TimetableGenerator.FIRST_ACTIVITY,
        firing_rules=firing_rules,
    )

    firing_rules2 = [
        FiringRule.lt(RULE_TYPE.DAILY_HOUR, 12),
        FiringRule.eq(RULE_TYPE.WEEK_DAY, DAY.MONDAY),
        FiringRule.gte(RULE_TYPE.DAILY_HOUR, 10),
    ]
    batching_rule2 = BatchingRule.from_task_id(
        TimetableGenerator.FIRST_ACTIVITY,
        firing_rules=firing_rules2,
    )

    assert batching_rule == batching_rule2

    # Add new firing rule to the end
    batching_rule = batching_rule.add_firing_rule(
        FiringRule.eq(RULE_TYPE.SIZE, "10"),
    )

    # Add new firing rule to the start
    batching_rule2 = replace(
        batching_rule2,
        firing_rules=[[FiringRule.eq(RULE_TYPE.SIZE, "10")], firing_rules2],
    )

    assert batching_rule == batching_rule2
    Settings.CHECK_FOR_TIMETABLE_EQUALITY = False
