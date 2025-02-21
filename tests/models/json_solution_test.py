from o2.models.json_report import JSONReport
from o2.optimizer import Optimizer
from o2.store import Store
from tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.test_helpers import replace_constraints
from tests.fixtures.timetable_generator import TimetableGenerator


def test_creating_json_solution(store: Store):
    store = replace_constraints(
        store, resources=ConstraintsGenerator.resource_constraints()
    )

    store.settings.max_iterations = 5
    store.settings.max_threads = 1

    optimizer = Optimizer(store)
    generator = optimizer.get_iteration_generator()
    next(generator)

    json_solution = JSONReport.from_store(store)
    # TODO: Improve Assertions
    assert json_solution is not None


def test_creating_json_solution_with_timetable_id(store: Store):
    store = replace_constraints(
        store,
        resources=ConstraintsGenerator.resource_constraints(
            resource_id=TimetableGenerator.RESOURCE_ID + "timetable"
        ),
    )

    store.settings.max_iterations = 5
    store.settings.max_threads = 1

    optimizer = Optimizer(store)
    generator = optimizer.get_iteration_generator()
    next(generator)

    json_solution = JSONReport.from_store(store)
    # TODO: Improve Assertions
    assert json_solution is not None
