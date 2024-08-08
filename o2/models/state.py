import datetime
import xml.etree.ElementTree as ET
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

import pytz
from bpdfr_simulation_engine.simulation_setup import SimDiffSetup

from o2.evaluator import Evaluator
from o2.SimDiffSetupFileless import SimDiffSetupFileless
from o2.simulation_runner import SimulationRunner

if TYPE_CHECKING:
    from o2.models.timetable import TimetableType


@dataclass(frozen=True)
class State:
    bpmn_definition: str
    bpmn_tree: ET.ElementTree

    timetable: "TimetableType"
    for_testing: bool = False

    def replaceTimetable(self, /, **changes):
        return replace(self, timetable=replace(self.timetable, **changes))

    def evaluate(self):
        (log, stats) = SimulationRunner.run_simulation(self)
        return Evaluator.evaluate_log(log, stats)

    def to_sim_diff_setup(self) -> SimDiffSetup:
        setup = SimDiffSetupFileless(
            "test",
            self.bpmn_definition,
            self.timetable,
            False,
            1000 if not self.for_testing else 100,
        )
        if self.for_testing:
            # For testing we start on 03.01.2000, a Monday
            starting_at_datetime = pytz.utc.localize(datetime.datetime(2000, 1, 3))
        else:
            starting_at_datetime = pytz.utc.localize(datetime.datetime.now())

        setup.set_starting_datetime(starting_at_datetime)

        return setup

    def get_name_of_task(self, task_id: str) -> str:
        node = self.bpmn_tree.find(f".//*[@id='{task_id}']")
        assert node is not None
        return node.attrib["name"]
