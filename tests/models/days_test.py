from o2.models.days import DAY, day_range


def test_day_range():
    day_range_result = day_range(DAY.MONDAY, DAY.WEDNESDAY)
    assert day_range_result == [DAY.MONDAY, DAY.TUESDAY, DAY.WEDNESDAY]


def test_same_day_range():
    day_range_result = day_range(DAY.MONDAY, DAY.MONDAY)
    assert day_range_result == [DAY.MONDAY]
