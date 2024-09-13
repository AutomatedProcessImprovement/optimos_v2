import datetime
import os
import uuid
from tempfile import mkstemp
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

from o2.hill_climber import HillClimber
from o2.models.json_report import JSONReport
from o2.models.legacy_approach import LegacyApproach
from o2.models.state import State
from o2.store import Store
from o2_server.types import ProcessingRequest


class OptimosService:
    def __init__(self):
        self.cancelled = False
        self.running = False
        self.id = str(uuid.uuid4())
        self.last_update = datetime.datetime.now()
        output_file, self.output_path = mkstemp(suffix=".zip", prefix="optimos_output_")
        os.fdopen(output_file).close()

    async def process(self, request: ProcessingRequest):
        """Process the optimization request."""
        self.running = True
        config = request["config"]

        num_instances = config["num_instances"]
        algorithm = config["algorithm"]
        approach = config["approach"]

        print(f"Num of instances: {num_instances}")
        print(f"Algorithm: {algorithm}")
        print(f"Approach: {approach}")

        timetable = request["timetable"]
        constraints = request["constraints"]
        bpmn_definition = request["bpmn_model"]

        bpmn_tree = ET.ElementTree(ET.fromstring(bpmn_definition))

        initial_state = State(
            bpmn_definition=bpmn_definition,
            bpmn_tree=bpmn_tree,
            timetable=timetable,
        )
        store = Store(
            state=initial_state,
            constraints=constraints,
        )
        # Settings
        store.settings.optimos_legacy_mode = True

        # Keep one cpu core free for other processes
        store.settings.max_threads = max(1, (os.cpu_count() or 1) - 1)
        store.settings.max_number_of_actions_to_select = store.settings.max_threads

        store.settings.legacy_approach = LegacyApproach.from_abbreviation(approach)

        store.settings.max_iterations = num_instances
        # We know we will be doing about `max_threads` actions per iteration, so we can set the max_non_improving_actions
        # to be the number of instances times the number of threads
        store.settings.max_non_improving_actions = (
            num_instances * store.settings.max_threads
        )

        # Create base evaluation
        store.evaluate()
        # Upload initial evaluation
        self.iteration_callback(store)

        hill_climber = HillClimber(store)
        generator = hill_climber.get_iteration_generator()
        print("Created Store")
        for _ in generator:
            if self.cancelled:
                print("Optimization Cancelled!")
                break

            print("Finished Iteration")
            self.iteration_callback(store)
        self.iteration_callback(
            store,
            last_iteration=True,
        )
        self.running = False

    def iteration_callback(self, store: Store, last_iteration=False):
        """Write Iteration to file."""
        json_solutions = JSONReport.from_store(store, is_final=last_iteration)
        json_content = json_solutions.to_json()

        with ZipFile(self.output_path, "w", compression=ZIP_DEFLATED) as zipf:
            zipf.writestr("result.json", json_content)
