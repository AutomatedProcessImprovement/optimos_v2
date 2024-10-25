from o2.models.solution_tree import SolutionTree
from o2.models.state import State
from o2.pareto_front import ParetoFront
from o2.store import Store
from tests.fixtures.mock_action import MockAction
from tests.fixtures.test_helpers import create_mock_solution


def test_add_solution(one_task_state: State):
    tree = SolutionTree()
    solution = create_mock_solution(one_task_state, 5, 5)

    tree.add_solution(solution)
    assert tree.solution_lookup[solution.id] == solution
    assert list(tree.solution_lookup.keys()) == [solution.id]


def test_check_if_already_done(one_task_store: Store):
    tree = SolutionTree()
    base_solution = one_task_store.base_solution
    solution = create_mock_solution(one_task_store.base_state, 5, 5)
    solution_action = solution.last_action
    random_action = MockAction()

    tree.add_solution(solution)
    assert tree.check_if_already_done(base_solution, solution_action) is True
    assert tree.check_if_already_done(base_solution, random_action) is False


def test_get_index_of_solution(one_task_state: State):
    tree = SolutionTree()
    solution1 = create_mock_solution(one_task_state, 5, 5)
    solution2 = create_mock_solution(one_task_state, 5, 5)
    solution3 = create_mock_solution(one_task_state, 5, 5)

    tree.add_solution(solution1)
    tree.add_solution(solution2)
    tree.add_solution(solution3)

    assert tree.get_index_of_solution(solution1) == 0
    assert tree.get_index_of_solution(solution2) == 1
    assert tree.get_index_of_solution(solution3) == 2


def test_get_nearest_solution_origin(one_task_store: Store):
    tree = SolutionTree()

    origin_solution = create_mock_solution(one_task_store.base_state, 0, 0)
    solution1 = create_mock_solution(one_task_store.base_state, 5, 5)
    solution2 = create_mock_solution(one_task_store.base_state, 3, 3)
    solution3 = create_mock_solution(one_task_store.base_state, 10, 10)

    origin_pareto_front = ParetoFront()
    origin_pareto_front.add(origin_solution)

    tree.add_solution(solution1)
    tree.add_solution(solution2)
    tree.add_solution(solution3)

    assert tree.get_nearest_solution(origin_pareto_front) == solution2


def test_get_nearest_solution_origin_max_distance(one_task_store: Store):
    tree = SolutionTree()

    origin_solution = create_mock_solution(one_task_store.base_state, 0, 0)
    solution1 = create_mock_solution(one_task_store.base_state, 5, 5)
    solution2 = create_mock_solution(one_task_store.base_state, 3, 3)
    solution3 = create_mock_solution(one_task_store.base_state, 10, 10)

    distance = solution2.evaluation.distance_to(origin_solution.evaluation)

    origin_pareto_front = ParetoFront()
    origin_pareto_front.add(origin_solution)

    tree.add_solution(solution1)
    tree.add_solution(solution2)
    tree.add_solution(solution3)

    assert tree.get_nearest_solution(origin_pareto_front, max_distance=2) is None
    assert (
        tree.get_nearest_solution(origin_pareto_front, max_distance=distance)
        is solution2
    )


def test_get_nearest_solution_pareto_front(one_task_store: Store):
    tree = SolutionTree()

    solution1 = create_mock_solution(one_task_store.base_state, 5, 5)
    solution2 = create_mock_solution(one_task_store.base_state, 100, 100)
    solution3 = create_mock_solution(one_task_store.base_state, 10, 10)

    pareto_front = ParetoFront()
    pareto_front.add(solution1)
    pareto_front.add(solution2)

    tree.add_solution(solution1)
    tree.add_solution(solution2)
    tree.add_solution(solution3)

    # Latest pareto solution is the "nearest"
    assert tree.get_nearest_solution(pareto_front) == solution2


def test_get_nearest_solution_multiple_pareto_entries(one_task_store: Store):
    tree = SolutionTree()

    pareto_solution1 = create_mock_solution(one_task_store.base_state, 3, 3)
    pareto_solution2 = create_mock_solution(one_task_store.base_state, 5, 5)
    pareto_solution3 = create_mock_solution(one_task_store.base_state, 10, 10)
    tree_solution1 = create_mock_solution(one_task_store.base_state, 2, 2)
    tree_solution2 = create_mock_solution(one_task_store.base_state, 5, 6)
    tree_solution3 = create_mock_solution(one_task_store.base_state, 6, 6)

    pareto_front = ParetoFront()
    pareto_front.add(pareto_solution1)
    pareto_front.add(pareto_solution2)
    pareto_front.add(pareto_solution3)

    tree.add_solution(tree_solution1)
    tree.add_solution(tree_solution2)
    tree.add_solution(tree_solution3)

    # tree_solution2 -> pareto_solution2 is the nearest
    assert tree.get_nearest_solution(pareto_front) == tree_solution2


def test_pop_nearest_solution(one_task_store: Store):
    tree = SolutionTree()

    solution1 = create_mock_solution(one_task_store.base_state, 5, 5)
    solution2 = create_mock_solution(one_task_store.base_state, 3, 3)
    solution3 = create_mock_solution(one_task_store.base_state, 10, 10)

    tree.add_solution(solution1)
    tree.add_solution(solution2)
    tree.add_solution(solution3)

    pareto_front = ParetoFront()
    pareto_front.add(solution1)

    assert tree.pop_nearest_solution(pareto_front) == solution1
    assert tree.pop_nearest_solution(pareto_front) == solution2
    assert tree.pop_nearest_solution(pareto_front) == solution3
    assert tree.pop_nearest_solution(pareto_front) is None

    assert tree.solution_lookup[solution1.id] is None
    assert tree.solution_lookup[solution2.id] is None
    assert tree.solution_lookup[solution3.id] is None
    assert solution1.id in tree.solution_lookup
    assert solution2.id in tree.solution_lookup
    assert solution3.id in tree.solution_lookup
