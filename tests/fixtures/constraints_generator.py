import io
import xml.etree.ElementTree as ET

from o2.types.constraints import (
    BATCH_TYPE,
    RULE_TYPE,
    ConstraintsType,
    DailyHourRuleConstraints,
    ReadyWtRuleConstraints,
    SizeRuleConstraints,
    WeekDayRuleConstraints,
)
from o2.types.days import DAY


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
    def add_size_constraint(
        self, optimal_duration=5, optimal_duration_bonus=0.75, min_size=0, max_size=10
    ):
        self.constraints.batching_constraints.append(
            SizeRuleConstraints(
                id=self.SIMPLE_CONSTRAINT_ID,
                tasks=[task.attrib["id"] for task in self.tasks],
                batch_type=BATCH_TYPE.PARALLEL,
                rule_type=RULE_TYPE.SIZE,
                duration_fn=f"0.2*(size - {optimal_duration})**2 + {optimal_duration_bonus}",
                min_size=min_size,
                max_size=max_size,
            )
        )
        return self

    def add_ready_wt_constraint(self):
        self.constraints.batching_constraints.append(
            ReadyWtRuleConstraints(
                id=self.SIMPLE_CONSTRAINT_ID,
                tasks=[task.attrib["id"] for task in self.tasks],
                batch_type=BATCH_TYPE.PARALLEL,
                rule_type=RULE_TYPE.READY_WT,
                min_wt=0,
                max_wt=24 * 60,
            )
        )
        return self

    def add_large_wt_constraint(self):
        self.constraints.batching_constraints.append(
            ReadyWtRuleConstraints(
                id=self.SIMPLE_CONSTRAINT_ID,
                tasks=[task.attrib["id"] for task in self.tasks],
                batch_type=BATCH_TYPE.PARALLEL,
                rule_type=RULE_TYPE.LARGE_WT,
                min_wt=0,
                max_wt=24 * 60,
            )
        )
        return self

    def add_week_day_constraint(self):
        self.constraints.batching_constraints.append(
            WeekDayRuleConstraints(
                id=self.SIMPLE_CONSTRAINT_ID,
                tasks=[task.attrib["id"] for task in self.tasks],
                batch_type=BATCH_TYPE.PARALLEL,
                rule_type=RULE_TYPE.WEEK_DAY,
                allowed_days=list(DAY),
            )
        )
        return self

    def add_daily_hour_constraint(self):
        self.constraints.batching_constraints.append(
            DailyHourRuleConstraints(
                id=self.SIMPLE_CONSTRAINT_ID,
                tasks=[task.attrib["id"] for task in self.tasks],
                batch_type=BATCH_TYPE.PARALLEL,
                rule_type=RULE_TYPE.DAILY_HOUR,
                allowed_hours=list(range(24)),
            )
        )
        return self

    def generate(self):
        self.add_ready_wt_constraint()
        self.add_large_wt_constraint()
        self.add_week_day_constraint()
        self.add_daily_hour_constraint()
        self.add_size_constraint()
        return self.constraints
