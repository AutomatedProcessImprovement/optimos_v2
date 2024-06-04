from o2.types.constraints import BATCH_TYPE, RULE_TYPE, ConstraintsType, SizeRuleConstraints
from o2.types.timetable import TimetableType


class ConstraintsGenerator:
    SIMPLE_CONSTRAINT_ID = "simple_constraint"

    def __init__(self, timetable: TimetableType):
        self.constraints = ConstraintsType([])
        self.timetable = timetable

    # Add a size constraint to the constraints
    def add_size_constraint(self):
        self.constraints.batching_constraints.append(SizeRuleConstraints(
            id=self.SIMPLE_CONSTRAINT_ID,
            tasks=[resources.id for resources in self.timetable.resource_profiles],
            batch_type=BATCH_TYPE.PARALLEL,
            rule_type=RULE_TYPE.SIZE,
            duration_fn="0.005*(size - 5)**2 + 0.8",
            min_size=5,
            max_size=10
        ))
    def generate(self):
        self.add_size_constraint()
        return self.constraints