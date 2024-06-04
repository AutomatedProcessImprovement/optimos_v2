import pytest
import os
from o2.types.state import State
from tests.fixtures.timetable_generator import TimeTableGenerator


BPMN_PATH = "./tests/fixtures/SimpleLoop.bpmn"


@pytest.fixture
def state():
    bpmn_content = open(BPMN_PATH, "r").read()
    return State(
        bpmn_definition= bpmn_content,
        timetable=TimeTableGenerator(bpmn_content).generate()
    )