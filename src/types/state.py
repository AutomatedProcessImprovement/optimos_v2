from dataclasses import dataclass, replace, asdict
import datetime
import io
import pytz
from src.SimDiffSetupFileless import SimDiffSetupFileless
from src.evaluator import Evaluator
from src.simulation_runner import SimulationRunner
from src.types.constraints import ConstraintsType
from src.types.timetable import TimetableType
from bpdfr_simulation_engine.simulation_setup import SimDiffSetup
from json import dumps


@dataclass(frozen=True)
class State:
    bpmn_definition: str

    constraints: ConstraintsType
    timetable: TimetableType

    def replaceConstraints(self, /, **changes):
        return replace(self, constraints=replace(self.constraints, **changes))

    def replaceTimetable(self, /, **changes):
        return replace(self, timetable=replace(self.timetable, **changes))

    def evaluate(self):
        (log, stats) = SimulationRunner.run_simulation(self)
        return Evaluator.evaluateLog(log, stats)

    def to_sim_diff_setup(self) -> SimDiffSetup:

        setup = SimDiffSetupFileless(
            "test", self.bpmn_definition, self.timetable, False, 1000
        )
        starting_at_datetime = pytz.utc.localize(datetime.datetime.now())

        setup.set_starting_datetime(starting_at_datetime)

        return setup
