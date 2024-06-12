import io
from o2.types.constraints import (
    BATCH_TYPE,
    RULE_TYPE,
    ConstraintsType,
    SizeRuleConstraints,
)
from o2.types.timetable import TimetableType
import xml.etree.ElementTree as ET


class ConstraintsGenerator:
    SIMPLE_CONSTRAINT_ID = "simple_constraint"

    def __init__(self, bpmn: str):
        self.constraints = ConstraintsType([])
        fileIo = io.StringIO()
        fileIo.write(bpmn)
        fileIo.seek(0)
        self.bpmn = ET.parse(fileIo)
        self.bpmnRoot = self.bpmn.getroot()
        # Get all the Elements of kind bpmn:task in bpmn:process
        self.tasks = self.bpmnRoot.findall(
            ".//{http://www.omg.org/spec/BPMN/20100524/MODEL}task"
        )

    # Add a size constraint to the constraints
    def add_size_constraint(self, optimal_duration=5):
        self.constraints.batching_constraints.append(
            SizeRuleConstraints(
                id=self.SIMPLE_CONSTRAINT_ID,
                tasks=[task.attrib["id"] for task in self.tasks],
                batch_type=BATCH_TYPE.PARALLEL,
                rule_type=RULE_TYPE.SIZE,
                duration_fn=f"0.005*(size - {optimal_duration})**2 + 0.8",
                min_size=2,
                max_size=10,
            )
        )
        return self

    def generate(self):
        self.add_size_constraint()
        return self.constraints
