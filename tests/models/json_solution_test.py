from o2.hill_climber import HillClimber
from o2.models.json_solution import JSONSolutions
from o2.store import Store
from tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.timetable_generator import TimetableGenerator


def test_creating_json_solution(store: Store):
    store.replaceConstraints(resources=ConstraintsGenerator.resource_constraints())
    # Base Evaluation
    store.evaluate()
    hill_climber = HillClimber(store, max_parallel=1, max_iter=5)
    generator = hill_climber.get_iteration_generator()
    next(generator)

    json_solution = JSONSolutions.from_store(store)
    assert json_solution is not None


def test_creating_json_solution_with_timetable_id(store: Store):
    store.replaceConstraints(
        resources=ConstraintsGenerator.resource_constraints(
            resource_id=TimetableGenerator.RESOURCE_ID + "timetable"
        )
    )
    # Base Evaluation
    store.evaluate()
    hill_climber = HillClimber(store, max_parallel=1, max_iter=5)
    generator = hill_climber.get_iteration_generator()
    next(generator)

    json_solution = JSONSolutions.from_store(store)
    assert json_solution is not None
