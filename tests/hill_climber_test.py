from o2.hill_climber import HillClimber
from o2.store import Store
from optimos_v2.o2.types.constraints import BATCH_TYPE, RULE_TYPE
from optimos_v2.o2.types.timetable import (
    COMPARATOR,
    BatchingRule,
    Distribution,
    FiringRule,
)
from tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.timetable_generator import TimetableGenerator


def test_hill_climber_simple(one_task_store: Store):
    store = one_task_store

    store.replaceTimetable(
        batch_processing=[
            TimetableGenerator.batching_size_rule(
                TimetableGenerator.FIRST_ACTIVITY, 10, 6
            )
        ]
    )

    store.replaceConstraints(
        batching_constraints=ConstraintsGenerator(store.state.bpmn_definition)
        # We don't allow removal of the batching
        .add_size_constraint(optimal_duration=5, optimal_duration_bonus=0.1, min_size=1)
        .constraints.batching_constraints
    )

    hill_climber = HillClimber(store)
    hill_climber.solve()

    # 3x Decrease Batching Size (10 -> 9 -> 8 -> 7)
    assert len(store.previous_actions) == 3