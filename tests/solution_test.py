from o2.models.settings import Settings
from o2.models.solution import Solution
from o2.models.state import State
from tests.fixtures.mock_action import MockAction, MockActionParamsType
from tests.fixtures.test_helpers import create_mock_solution


def test_solution_equality(one_task_state: State):
    solution1 = create_mock_solution(one_task_state, 5, 5, force_uniqueness=False)
    solution2 = create_mock_solution(one_task_state, 5, 5, force_uniqueness=False)

    assert solution1.id == solution2.id
    assert solution1 == solution2

    solution_set = {solution1, solution2}
    assert len(solution_set) == 1

    solution3 = Solution.from_parent(
        solution1, MockAction(params=MockActionParamsType(random_string="STR1"))
    )
    solution4 = Solution.from_parent(
        solution2, MockAction(params=MockActionParamsType(random_string="STR2"))
    )

    assert solution3.id != solution4.id
    assert solution3 != solution4


def test_solution_equality_with_timetable(one_task_state: State):
    Settings.CHECK_FOR_TIMETABLE_EQUALITY = True
    solution1 = create_mock_solution(one_task_state, 5, 5, force_uniqueness=False)
    solution2 = create_mock_solution(one_task_state, 5, 5, force_uniqueness=False)

    assert solution1.id == solution2.id
    assert solution1 == solution2
    assert hash(solution1) == hash(solution2)

    solution3 = Solution.from_parent(
        solution1, MockAction(params=MockActionParamsType(random_string="STR1"))
    )
    solution4 = Solution.from_parent(
        solution2, MockAction(params=MockActionParamsType(random_string="STR2"))
    )

    # Ids are still soly based on action history
    assert solution3.id != solution4.id
    assert hash(solution3) == hash(solution4)
    assert solution3 == solution4

    solution_set = {solution1, solution2, solution3, solution4}
    assert len(solution_set) == 1

    Settings.CHECK_FOR_TIMETABLE_EQUALITY = False
