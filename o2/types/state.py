from dataclasses import dataclass, replace, asdict
import datetime
import io
import pytz
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from o2.types.timetable import TimetableType
from o2.SimDiffSetupFileless import SimDiffSetupFileless
from o2.evaluator import Evaluator
from o2.simulation_runner import SimulationRunner
from o2.types.constraints import ConstraintsType
from bpdfr_simulation_engine.simulation_setup import SimDiffSetup
from json import dumps


@dataclass(frozen=True)
class State:
    bpmn_definition: str

    timetable: "TimetableType"
    for_testing: bool = False

    def replaceTimetable(self, /, **changes):
        return replace(self, timetable=replace(self.timetable, **changes))

    def evaluate(self):
        (log, stats) = SimulationRunner.run_simulation(self)
        return Evaluator.evaluateLog(log, stats)

    def to_sim_diff_setup(self) -> SimDiffSetup:
        setup = SimDiffSetupFileless(
            "test",
            self.bpmn_definition,
            self.timetable,
            False,
            1000 if not self.for_testing else 100,
        )
        starting_at_datetime = pytz.utc.localize(datetime.datetime.now())

        setup.set_starting_datetime(starting_at_datetime)

        return setup
