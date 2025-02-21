from o2.optimizer import Optimizer
from o2.models.settings import AgentType
from o2.store import Store
from tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.test_helpers import replace_constraints, replace_timetable
from tests.fixtures.timetable_generator import TimetableGenerator


def test_optimizer_simple(one_task_store: Store):
    store = replace_timetable(
        one_task_store,
        batch_processing=[
            TimetableGenerator.batching_size_rule(
                TimetableGenerator.FIRST_ACTIVITY, 10, 6
            )
        ],
    )

    store = replace_constraints(
        store,
        batching_constraints=ConstraintsGenerator(store.base_state.bpmn_definition)
        # We don't allow removal of the batching
        .add_size_constraint(optimal_duration=5, optimal_duration_bonus=0.1, min_size=1)
        .constraints.batching_constraints,
    )

    store.settings.throw_on_iteration_errors = True
    store.settings.disable_parallel_evaluation = True
    store.settings.max_iterations = 3
    store.settings.max_threads = 1

    optimizer = Optimizer(store)
    optimizer.solve()

    # 3x Decrease Batching Size (10 -> 9 -> 8 -> 7)
    # TODO: Fix
    # assert len(store.previous_actions) == 3


def test_optimizer_batching(one_task_store: Store):
    store = replace_timetable(
        one_task_store,
        batch_processing=[
            TimetableGenerator.batching_size_rule(
                TimetableGenerator.FIRST_ACTIVITY, 10, 1
            )
        ],
    )

    store = replace_constraints(
        store,
        batching_constraints=ConstraintsGenerator(store.base_state.bpmn_definition)
        # We don't allow removal of the batching
        .add_size_constraint(optimal_duration=5, optimal_duration_bonus=0.1, min_size=1)
        .constraints.batching_constraints,
    )

    store.settings.throw_on_iteration_errors = True
    store.settings.max_iterations = 3
    store.settings.max_threads = 1
    store.settings.disable_parallel_evaluation = True
    store.settings.optimos_legacy_mode = False

    store.settings.batching_only = True

    optimizer = Optimizer(store)
    optimizer.solve()


def test_optimizer_ppo(one_task_store: Store):
    store = replace_timetable(
        one_task_store,
        batch_processing=[
            TimetableGenerator.batching_size_rule(
                TimetableGenerator.FIRST_ACTIVITY, 10, 1
            )
        ],
    )

    store = replace_constraints(
        store,
        batching_constraints=ConstraintsGenerator(store.base_state.bpmn_definition)
        # We don't allow removal of the batching
        .add_size_constraint(optimal_duration=5, optimal_duration_bonus=0.1, min_size=1)
        .constraints.batching_constraints,
    )

    store.settings.throw_on_iteration_errors = True
    store.settings.max_iterations = 3
    store.settings.max_threads = 1
    store.settings.disable_parallel_evaluation = True
    store.settings.optimos_legacy_mode = False

    store.settings.agent = AgentType.PROXIMAL_POLICY_OPTIMIZATION

    optimizer = Optimizer(store)
    optimizer.solve()
