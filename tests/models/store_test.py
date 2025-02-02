from o2.actions.base_actions.add_datetime_rule_base_action import (
    AddDateTimeRuleAction,
    AddDateTimeRuleBaseActionParamsType,
)
from o2.models.solution import Solution
from o2.models.time_period import TimePeriod
from o2.pareto_front import FRONT_STATUS
from o2.store import Store
from tests.fixtures.timetable_generator import TimetableGenerator


def test_store_invalid_solution_handling(one_task_store: Store):
    store = Store.from_state_and_constraints(
        one_task_store.base_state, one_task_store.constraints
    )

    invalid_action = AddDateTimeRuleAction(
        AddDateTimeRuleBaseActionParamsType(
            task_id=TimetableGenerator.FIRST_ACTIVITY,
            # NOTE the invalid time period
            time_period=TimePeriod.from_start_end(start=-12, end=0),
        )
    )
    initial_solution = Solution.from_parent(store.solution, invalid_action)
    status, solution = store.try_solution(initial_solution)

    assert status == FRONT_STATUS.INVALID
    assert not solution.is_valid

    _, not_chosen = store.process_many_solutions([solution], None)
    assert store.solution_tree.solution_lookup[solution.id] is None
    assert len(not_chosen) == 1
    assert not_chosen[0][0] == FRONT_STATUS.INVALID

    assert store.is_tabu(invalid_action)
