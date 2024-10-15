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
        bpmn_tree=ElementTree.parse(SIMPLE_LOOP_BPMN_PATH),
        timetable=TimetableGenerator(bpmn_content).generate_simple(),
        for_testing=True,
    )


@pytest.fixture(scope="function")
def one_task_state():
    bpmn_content = open(ONE_TASK_BPMN_PATH).read()
    return State(
        bpmn_definition=bpmn_content,
        bpmn_tree=ElementTree.parse(ONE_TASK_BPMN_PATH),
        timetable=TimetableGenerator(bpmn_content).generate_simple(),
        for_testing=True,
    )


@pytest.fixture(scope="function")
def one_task_solution(one_task_state: State):
    evaluation = one_task_state.evaluate()
    return Solution(
        evaluation=evaluation, state=one_task_state, parent_state=None, actions=[]
    )


@pytest.fixture(scope="function")
def one_task_store(one_task_solution: Solution):
    return Store(
        solution=one_task_solution,
        constraints=ConstraintsGenerator(
            one_task_solution.state.bpmn_definition
        ).generate(),
    )


@pytest.fixture(scope="function")
def two_tasks_state():
    bpmn_content = open(TWO_TASKS_BPMN_PATH).read()
    return State(
        bpmn_definition=bpmn_content,
        bpmn_tree=ElementTree.parse(TWO_TASKS_BPMN_PATH),
        timetable=TimetableGenerator(bpmn_content).generate_simple(),
        for_testing=True,
    )


@pytest.fixture(scope="function")
def two_tasks_solution(two_tasks_state: State):
    evaluation = two_tasks_state.evaluate()
    return Solution(
        evaluation=evaluation, state=two_tasks_state, parent_state=None, actions=[]
    )


@pytest.fixture(scope="function")
def two_tasks_store(two_tasks_solution: Solution):
    return Store(
        solution=two_tasks_solution,
        constraints=ConstraintsGenerator(
            two_tasks_solution.state.bpmn_definition
        ).generate(),
    )


@pytest.fixture(scope="function")
def batching_state():
    bpmn_content = open(SIMPLE_LOOP_BPMN_PATH).read()
    return State(
        bpmn_definition=bpmn_content,
        bpmn_tree=ElementTree.parse(SIMPLE_LOOP_BPMN_PATH),
        timetable=TimetableGenerator(bpmn_content).generate_simple(
            include_batching=True
        ),
        for_testing=True,
    )


@pytest.fixture(scope="function")
def constraints():
    bpmn_content = open(SIMPLE_LOOP_BPMN_PATH).read()
    return ConstraintsGenerator(bpmn_content).generate()


@pytest.fixture(scope="function")
def batching_solution(batching_state: State):
    evaluation = batching_state.evaluate()
    return Solution(
        evaluation=evaluation, state=batching_state, parent_state=None, actions=[]
    )


@pytest.fixture(scope="function")
def store(batching_solution: Solution, constraints: ConstraintsType):
    return Store(solution=batching_solution, constraints=constraints)
