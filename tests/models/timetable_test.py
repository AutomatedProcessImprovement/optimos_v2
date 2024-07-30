from o2.models.days import DAY
from o2.models.timetable import ResourceCalendar, TimePeriod


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
            TimePeriod(DAY.MONDAY, DAY.MONDAY, "08:00", "12:00"),
            TimePeriod(DAY.MONDAY, DAY.MONDAY, "11:00", "23:00"),
        ],
    )

    assert not resource_calendar.is_valid()


def test_resource_calendar_verify_end_before_begin():
    resource_calendar = ResourceCalendar(
        id="1",
        name="Resource Calendar",
        time_periods=[
            TimePeriod(DAY.MONDAY, DAY.MONDAY, "12:00", "08:00"),
        ],
    )

    assert not resource_calendar.is_valid()
