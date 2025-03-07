import xml.etree.ElementTree as ElementTree

import pytest

from o2.models.constraints import ConstraintsType
from o2.models.solution import Solution
from o2.models.state import State
from o2.store import Store
from tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.timetable_generator import TimetableGenerator

SIMPLE_LOOP_BPMN_PATH = "./tests/fixtures/SimpleLoop.bpmn"
ONE_TASK_BPMN_PATH = "./tests/fixtures/OneTask.bpmn"
TWO_TASKS_BPMN_PATH = "./tests/fixtures/TwoTasks.bpmn"


@pytest.fixture(scope="function")
def simple_state():
    bpmn_content = open(SIMPLE_LOOP_BPMN_PATH).read()
    return State(
        bpmn_definition=bpmn_content,
        timetable=TimetableGenerator(bpmn_content).generate_simple(),
        for_testing=True,
    )


@pytest.fixture(scope="function")
def one_task_state():
    bpmn_content = open(ONE_TASK_BPMN_PATH).read()
    return State(
        bpmn_definition=bpmn_content,
        timetable=TimetableGenerator(bpmn_content).generate_simple(),
        for_testing=True,
    )


@pytest.fixture(scope="function")
def one_task_solution(one_task_state: State):
    evaluation = one_task_state.evaluate()
    return Solution(evaluation=evaluation, state=one_task_state, actions=[])


@pytest.fixture(scope="function")
def one_task_store(one_task_solution: Solution):
    return Store(
        solution=one_task_solution,
        constraints=ConstraintsGenerator(one_task_solution.state.bpmn_definition).generate(),
    )


@pytest.fixture(scope="function")
def two_tasks_state():
    bpmn_content = open(TWO_TASKS_BPMN_PATH).read()
    return State(
        bpmn_definition=bpmn_content,
        timetable=TimetableGenerator(bpmn_content).generate_simple(),
        for_testing=True,
    )


@pytest.fixture(scope="function")
def two_tasks_solution(two_tasks_state: State):
    evaluation = two_tasks_state.evaluate()
    return Solution(evaluation=evaluation, state=two_tasks_state, actions=[])


@pytest.fixture(scope="function")
def two_tasks_store(two_tasks_solution: Solution):
    return Store(
        solution=two_tasks_solution,
        constraints=ConstraintsGenerator(two_tasks_solution.state.bpmn_definition).generate(),
    )


@pytest.fixture(scope="function")
def batching_state():
    bpmn_content = open(SIMPLE_LOOP_BPMN_PATH).read()
    return State(
        bpmn_definition=bpmn_content,
        timetable=TimetableGenerator(bpmn_content).generate_simple(include_batching=True),
        for_testing=True,
    )


@pytest.fixture(scope="function")
def constraints():
    bpmn_content = open(SIMPLE_LOOP_BPMN_PATH).read()
    return ConstraintsGenerator(bpmn_content).generate()


@pytest.fixture(scope="function")
def batching_solution(batching_state: State):
    evaluation = batching_state.evaluate()
    return Solution(evaluation=evaluation, state=batching_state, actions=[])


@pytest.fixture(scope="function")
def store(batching_solution: Solution, constraints: ConstraintsType):
    return Store(solution=batching_solution, constraints=constraints)


@pytest.fixture(scope="function")
def multi_resource_state(one_task_state: State):
    return one_task_state.replace_timetable(
        resource_calendars=TimetableGenerator.resource_calendars_multi_resource(3),
        resource_profiles=TimetableGenerator.resource_pools_multi_resource(
            [TimetableGenerator.FIRST_ACTIVITY], 3
        ),
        task_resource_distribution=TimetableGenerator.task_resource_distribution_multi_resource(
            [TimetableGenerator.FIRST_ACTIVITY], 3
        ),
    )
