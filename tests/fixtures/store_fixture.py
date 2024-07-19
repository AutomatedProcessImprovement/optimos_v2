import pytest
import os
from o2.types.state import State
from o2.store import Store
from o2.types.constraints import ConstraintsType
from tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.timetable_generator import TimetableGenerator
import xml.etree.ElementTree as ET


SIMPLE_LOOP_BPMN_PATH = "./tests/fixtures/SimpleLoop.bpmn"
ONE_TASK_BPMN_PATH = "./tests/fixtures/OneTask.bpmn"
TWO_TASKS_BPMN_PATH = "./tests/fixtures/TwoTasks.bpmn"


@pytest.fixture(scope="function")
def simple_state():
    print("Creating simple_state")
    bpmn_content = open(SIMPLE_LOOP_BPMN_PATH).read()
    return State(
        bpmn_definition=bpmn_content,
        bpmn_tree=ET.parse(SIMPLE_LOOP_BPMN_PATH),
        timetable=TimetableGenerator(bpmn_content).generate_simple(),
        for_testing=True,
    )


@pytest.fixture(scope="function")
def one_task_state():
    print("Creating one_task_state")
    bpmn_content = open(ONE_TASK_BPMN_PATH).read()
    return State(
        bpmn_definition=bpmn_content,
        bpmn_tree=ET.parse(ONE_TASK_BPMN_PATH),
        timetable=TimetableGenerator(bpmn_content).generate_simple(),
        for_testing=True,
    )


@pytest.fixture(scope="function")
def one_task_store(one_task_state: State):
    print("Creating one_task_store")
    return Store(
        state=one_task_state,
        constraints=ConstraintsGenerator(one_task_state.bpmn_definition).generate(),
    )


@pytest.fixture(scope="function")
def two_tasks_state():
    print("Creating two_tasks_state")
    bpmn_content = open(TWO_TASKS_BPMN_PATH).read()
    return State(
        bpmn_definition=bpmn_content,
        bpmn_tree=ET.parse(TWO_TASKS_BPMN_PATH),
        timetable=TimetableGenerator(bpmn_content).generate_simple(),
        for_testing=True,
    )


@pytest.fixture(scope="function")
def two_tasks_store(two_tasks_state: State):
    print("Creating two_tasks_store")
    return Store(
        state=two_tasks_state,
        constraints=ConstraintsGenerator(two_tasks_state.bpmn_definition).generate(),
    )


@pytest.fixture(scope="function")
def batching_state():
    print("Creating batching_state")
    bpmn_content = open(SIMPLE_LOOP_BPMN_PATH).read()
    return State(
        bpmn_definition=bpmn_content,
        bpmn_tree=ET.parse(SIMPLE_LOOP_BPMN_PATH),
        timetable=TimetableGenerator(bpmn_content).generate_simple(
            include_batching=True
        ),
        for_testing=True,
    )


@pytest.fixture(scope="function")
def constraints():
    print("Creating constraints")
    bpmn_content = open(SIMPLE_LOOP_BPMN_PATH).read()
    return ConstraintsGenerator(bpmn_content).generate()


@pytest.fixture(scope="function")
def store(batching_state: State, constraints: ConstraintsType):
    print("Creating store")
    return Store(
        state=batching_state,
        constraints=constraints,
    )
