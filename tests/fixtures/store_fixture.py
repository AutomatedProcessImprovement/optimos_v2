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


@pytest.fixture
def simple_state():
    bpmn_content = open(SIMPLE_LOOP_BPMN_PATH, "r").read()
    return State(
        bpmn_definition=bpmn_content,
        bpmn_tree=ET.parse(SIMPLE_LOOP_BPMN_PATH),
        timetable=TimetableGenerator(bpmn_content).generate_simple(),
        for_testing=True,
    )


@pytest.fixture
def one_task_state():
    bpmn_content = open(ONE_TASK_BPMN_PATH, "r").read()
    return State(
        bpmn_definition=bpmn_content,
        bpmn_tree=ET.parse(ONE_TASK_BPMN_PATH),
        timetable=TimetableGenerator(bpmn_content).generate_simple(),
        for_testing=True,
    )


@pytest.fixture
def one_task_store(one_task_state: State):
    return Store(
        state=one_task_state,
        constraints=ConstraintsGenerator(one_task_state.bpmn_definition).generate(),
    )


@pytest.fixture
def batching_state():
    bpmn_content = open(SIMPLE_LOOP_BPMN_PATH, "r").read()
    return State(
        bpmn_definition=bpmn_content,
        bpmn_tree=ET.parse(SIMPLE_LOOP_BPMN_PATH),
        timetable=TimetableGenerator(bpmn_content).generate_simple(
            include_batching=True
        ),
        for_testing=True,
    )


@pytest.fixture
def constraints():
    bpmn_content = open(SIMPLE_LOOP_BPMN_PATH, "r").read()
    return ConstraintsGenerator(bpmn_content).generate()


@pytest.fixture
def store(batching_state: State, constraints: ConstraintsType):
    return Store(
        state=batching_state,
        constraints=constraints,
    )
