import pytest
import os
from o2.types.state import State
from o2.store import Store
from optimos_v2.o2.types.constraints import ConstraintsType
from tests.fixtures.constraints_generator import ConstraintsGenerator
from tests.fixtures.timetable_generator import TimetableGenerator
import xml.etree.ElementTree as ET


BPMN_PATH = "./tests/fixtures/SimpleLoop.bpmn"


@pytest.fixture
def simple_state():
    bpmn_content = open(BPMN_PATH, "r").read()
    return State(
        bpmn_definition=bpmn_content,
        bpmn_tree=ET.parse(BPMN_PATH),
        timetable=TimetableGenerator(bpmn_content).generate_simple(),
        for_testing=True,
    )


@pytest.fixture
def batching_state():
    bpmn_content = open(BPMN_PATH, "r").read()
    return State(
        bpmn_definition=bpmn_content,
        bpmn_tree=ET.parse(BPMN_PATH),
        timetable=TimetableGenerator(bpmn_content).generate_simple(
            include_batching=True
        ),
        for_testing=True,
    )


@pytest.fixture
def constraints():
    bpmn_content = open(BPMN_PATH, "r").read()
    return ConstraintsGenerator(bpmn_content).generate()


@pytest.fixture
def store(batching_state: State, constraints: ConstraintsType):
    return Store(
        state=batching_state,
        constraints=constraints,
    )
