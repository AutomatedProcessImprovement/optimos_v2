from o2.hill_climber import HillClimber
from o2.models.json_report import JSONReport
from o2.store import Store
from tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.timetable_generator import TimetableGenerator


def test_creating_json_solution(store: Store):
    store.settings.max_iterations = 5
    store.settings.max_threads = 1

    store.replaceConstraints(resources=ConstraintsGenerator.resource_constraints())
    # Base Evaluation
    store.evaluate()
    hill_climber = HillClimber(store)
    generator = hill_climber.get_iteration_generator()
    next(generator)

    json_solution = JSONReport.from_store(store)
    assert json_solution is not None


def test_creating_json_solution_with_timetable_id(store: Store):
    store.settings.max_iterations = 5
    store.settings.max_threads = 1

    store.replaceConstraints(
        resources=ConstraintsGenerator.resource_constraints(
            resource_id=TimetableGenerator.RESOURCE_ID + "timetable"
        )
    )
    # Base Evaluation
    store.evaluate()
    hill_climber = HillClimber(store)
    generator = hill_climber.get_iteration_generator()
    next(generator)

    json_solution = JSONReport.from_store(store)
    assert json_solution is not None
