from o2.actions.new_actions.modify_size_rule_by_cost_action import (
    ModifySizeRuleByCostAction,
)
from o2.agents.tabu_agent import TabuAgent
from o2.models.self_rating import RATING, SelfRatingInput
from o2.store import Store
from tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.test_helpers import (
    assert_no_first_valid,
    first_valid,
    replace_constraints,
    replace_timetable,
)
from tests.fixtures.timetable_generator import TimetableGenerator


def test_self_rating_optimal_rule(one_task_store: Store):
    store = replace_timetable(
        one_task_store,
        batch_processing=[
            TimetableGenerator.batching_size_rule(TimetableGenerator.FIRST_ACTIVITY, 1)
        ],
        task_resource_distribution=TimetableGenerator.task_resource_distribution_simple(
            [TimetableGenerator.FIRST_ACTIVITY],
            # Long duration, therefore good to batch
            60 * 60 * 2,
        ),
    )

    store = replace_constraints(
        store,
        batching_constraints=[
            ConstraintsGenerator(store.base_state.bpmn_definition).size_constraint(
                [TimetableGenerator.FIRST_ACTIVITY],
                optimal_duration=3,
                optimal_duration_bonus=0.2,
            )
        ],
    )

    evaluations = TabuAgent.evaluate_rules(store)
    rating_input = SelfRatingInput.from_rule_solutions(store, evaluations)
    assert rating_input is not None
    rating, action = first_valid(
        store, ModifySizeRuleByCostAction.rate_self(store, rating_input)
    )
    assert rating == RATING.MEDIUM
    assert action is not None
    assert action.params["size_increment"] == 1  # type: ignore


def test_self_rating_non_optimal_rule_decrement(two_tasks_store: Store):
    store = replace_timetable(
        two_tasks_store,
        task_resource_distribution=(
            TimetableGenerator.task_resource_distribution_simple(
                # Short Task
                [TimetableGenerator.FIRST_ACTIVITY],
                1,
            )
            + TimetableGenerator.task_resource_distribution_simple(
                # Long Task
                [TimetableGenerator.SECOND_ACTIVITY],
                10,
            )
        ),
        batch_processing=[
            TimetableGenerator.batching_size_rule(TimetableGenerator.FIRST_ACTIVITY, 1),
            TimetableGenerator.batching_size_rule(
                TimetableGenerator.SECOND_ACTIVITY, 1
            ),
        ],
    )
    store = replace_constraints(
        store,
        batching_constraints=[
            ConstraintsGenerator(store.base_state.bpmn_definition).size_constraint(
                [
                    TimetableGenerator.FIRST_ACTIVITY,
                    TimetableGenerator.SECOND_ACTIVITY,
                ],
                max_size=10,
                min_size=1,
            )
        ],
    )

    evaluations = TabuAgent.evaluate_rules(store)
    rating_input = SelfRatingInput.from_rule_solutions(store, evaluations)
    assert rating_input is not None
    rating, action = first_valid(
        store, ModifySizeRuleByCostAction.rate_self(store, rating_input)
    )
    assert rating == RATING.MEDIUM
    assert action is not None
    assert (
        action.params["rule"].batching_rule_task_id  # type: ignore
        == TimetableGenerator.SECOND_ACTIVITY
    )
    assert action.params["size_increment"] == 1  # type: ignore
