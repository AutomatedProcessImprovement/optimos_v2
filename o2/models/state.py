import datetime
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, replace
from typing import TYPE_CHECKING

import pytz
from bpdfr_simulation_engine.simulation_setup import SimDiffSetup

from o2.actions.base_action import BaseAction
from o2.models.evaluation import Evaluation
from o2.simulation_runner import SimulationRunner
from o2.util.sim_diff_setup_fileless import SimDiffSetupFileless

if TYPE_CHECKING:
    from o2.models.timetable import TimetableType


@dataclass(frozen=True)
class State:
    """A state in the optimization process.

    It's mainly a container class for the timetable.

    The State should contain all information to run a simulation -- that's why it
    contains the BPMN definition as well.
    """

    bpmn_definition: str
    bpmn_tree: ET.ElementTree

    timetable: "TimetableType"
    # TODO: Move to setting class
    for_testing: bool = False

    def replace_timetable(self, /, **changes) -> "State":
        """Replace the timetable with the given changes."""
        return replace(self, timetable=replace(self.timetable, **changes))

    def evaluate(self, show_simulation_errors: bool = False) -> Evaluation:
        """Evaluate the current state."""
        result = SimulationRunner.run_simulation(self, show_simulation_errors)
        return Evaluation.from_run_simulation_result(
            self.timetable.get_hourly_rates(), result
        )

    def to_sim_diff_setup(self) -> SimDiffSetup:
        """Convert the state to a SimDiffSetup."""
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
        """Get the name of a task."""
        node = self.bpmn_tree.find(f".//*[@id='{task_id}']")
        assert node is not None
        return node.attrib["name"]
