from o2.actions.action_selector import ActionSelector
from o2.actions.modify_calendar_by_wt_action import ModifyCalendarByWTAction
from o2.actions.modify_daily_hour_rule_action import (
    ModifyDailyHourRuleAction,
    ModifyDailyHourRuleActionParamsType,
)
from o2.models.days import DAY
from o2.models.rule_selector import RuleSelector
from o2.models.self_rating import RATING, SelfRatingInput
from o2.models.timetable import ResourceCalendar, TimePeriod
from o2.store import Store
from o2.models.state import State
from tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.timetable_generator import TimetableGenerator


def test_simple_update(one_task_state: State):
    new_calendar = ResourceCalendar(
        id=TimetableGenerator.CALENDAR_ID,
        name="Updated Calendar",
        time_periods=[],
    )

    action = ModifyCalendarByWTAction(params={"updated_calendar": new_calendar})

    assert (
        one_task_state.timetable.get_calendar(TimetableGenerator.CALENDAR_ID).name  # type: ignore
        == TimetableGenerator.CALENDAR_ID
    )

    new_state = action.apply(one_task_state)

    assert (
        new_state.timetable.get_calendar(TimetableGenerator.CALENDAR_ID).name  # type: ignore
        == "Updated Calendar"
    )


def test_action_creation_simple_addition(one_task_store: Store):
    one_task_store.replaceTimetable(
        resource_calendars=TimetableGenerator.resource_calendars(8, 16, False)
    )

    evaluation, _ = one_task_store.evaluate()
    input = SelfRatingInput.from_base_evaluation(evaluation)

    rating, action = ModifyCalendarByWTAction.rate_self(one_task_store, input)

    assert action is not None
    monday_periods = action.params["updated_calendar"].get_periods_for_day(DAY.MONDAY)
    assert monday_periods == [
        TimePeriod(
            from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="07:00:00", end_time="16:00:00"
        )
    ]


def test_action_creation_simple_shift(one_task_store: Store):
    one_task_store.replaceTimetable(
        resource_calendars=TimetableGenerator.resource_calendars(8, 16, False)
    )
    one_task_store.replaceConstraints(
        resources=ConstraintsGenerator.resource_constraints(
            global_constraints=ConstraintsGenerator.global_constraints(
                # Restrict to 8 hours, so we cant just add a new hour
                max_consecutive_cap=8
            )
        )
    )

    evaluation, _ = one_task_store.evaluate()
    input = SelfRatingInput.from_base_evaluation(evaluation)

    rating, action = ModifyCalendarByWTAction.rate_self(one_task_store, input)

    assert action is not None
    monday_periods = action.params["updated_calendar"].get_periods_for_day(DAY.MONDAY)
    assert monday_periods == [
        TimePeriod(
            from_=DAY.MONDAY, to=DAY.MONDAY, begin_time="07:00:00", end_time="15:00:00"
        )
    ]


def test_other_days_not_affected(one_task_store: Store):
    one_task_store.replaceTimetable(
        resource_calendars=TimetableGenerator.resource_calendars(8, 16, False)
    )
    evaluation, _ = one_task_store.evaluate()
    input = SelfRatingInput.from_base_evaluation(evaluation)

    rating, action = ModifyCalendarByWTAction.rate_self(one_task_store, input)
    assert action is not None
    one_task_store.apply_action(action)
    new_calendar = one_task_store.state.timetable.get_calendar(
        TimetableGenerator.CALENDAR_ID
    )
    assert new_calendar is not None

    assert new_calendar.get_periods_for_day(DAY.TUESDAY) == [
        TimePeriod(
            from_=DAY.TUESDAY,
            to=DAY.TUESDAY,
            begin_time="08:00:00",
            end_time="16:00:00",
        )
    ]
