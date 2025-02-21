import datetime
import os
import uuid
from pprint import pprint
from tempfile import mkstemp
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

from o2.models.json_report import JSONReport
from o2.models.legacy_approach import LegacyApproach
from o2.models.state import State
from o2.optimizer import Optimizer
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

        print("New Request!")
        print("Config:")
        pprint(config)

        timetable = request["timetable"]
        constraints = request["constraints"]
        bpmn_definition = request["bpmn_model"]

        initial_state = State(
            bpmn_definition=bpmn_definition,
            timetable=timetable,
        )

        if config["num_cases"] is not None and config["num_cases"] > 0:
            initial_state.replace_timetable(total_cases=config["num_cases"])

        store = Store.from_state_and_constraints(
            initial_state,
            constraints,
        )
        store.name = config["scenario_name"]

        # Update settings

        # Keep one cpu core free for other processes (e.g. web request handling)
        store.settings.max_threads = max(1, (os.cpu_count() or 1) - 1)

        store.settings.optimos_legacy_mode = config["disable_batch_optimization"]

        # We limit the number of actions to select to the number of threads
        store.settings.max_number_of_actions_to_select = min(
            (config["max_actions_per_iteration"] or 1000), store.settings.max_threads
        )
        store.settings.legacy_approach = LegacyApproach.from_abbreviation(
            config["approach"]
        )
        store.settings.max_iterations = config["max_iterations"]
        store.settings.max_non_improving_actions = config["max_non_improving_actions"]
        store.settings.agent = config["agent"]

        # Upload initial evaluation
        self.iteration_callback(store)

        optimizer = Optimizer(store)
        generator = optimizer.get_iteration_generator()
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
