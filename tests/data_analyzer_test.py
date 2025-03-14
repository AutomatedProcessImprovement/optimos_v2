from o2.models.solution import Solution
from o2.models.state import State
from o2_evaluation.data_analyzer import handle_duplicates


def test_handle_duplicates(one_task_state: State):
    """Test the handle_duplicates function."""
    evaluation1 = one_task_state.evaluate()
    solution1 = Solution(actions=[], evaluation=evaluation1, state=one_task_state)
    evaluation2 = one_task_state.evaluate()
    solution2 = Solution(actions=[], evaluation=evaluation2, state=one_task_state)
    handle_duplicates([solution1, solution2])

    min_cycle_time = min(evaluation1.total_cycle_time, evaluation2.total_cycle_time)
    assert solution1.evaluation.total_cycle_time == min_cycle_time
    assert solution2.evaluation.total_cycle_time == min_cycle_time
