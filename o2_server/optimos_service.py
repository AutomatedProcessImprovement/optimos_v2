import datetime
import os
import traceback
import uuid
from pprint import pprint
from tempfile import mkstemp
from zipfile import ZIP_DEFLATED, ZipFile

from o2.models.json_report import JSONReport
from o2.models.legacy_approach import LegacyApproach
from o2.models.settings import Settings
from o2.models.state import State
from o2.optimizer import Optimizer
from o2.store import Store
from o2.util.logger import setup_logging
from o2_server.server_types import ProcessingRequest


class OptimosService:
    def __init__(self):
        self.cancelled = False
        self.running = False
        self.id = str(uuid.uuid4())
        self.last_update = datetime.datetime.now()
        output_file, self.output_path = mkstemp(suffix=".zip", prefix="optimos_output_")
        os.fdopen(output_file).close()

    def process(self, request: ProcessingRequest):
        """Process the optimization request."""
        self.running = True

        log_file_name = f"optimos_server_{self.id}.log"
        Settings.LOG_FILE = log_file_name
        setup_logging()

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

        Settings.MAX_THREADS_MEDIAN_CALCULATION = 1

        store.settings.max_solutions = config["max_solutions"]
        store.settings.max_non_improving_actions = config["max_non_improving_actions"]

        store.settings.log_to_tensor_board = False
        store.settings.iterations_per_solution = None
        store.settings.max_variants_per_action = (
            # We set it to -1, because later we'll set action_variation_selection to
            # ActionVariationSelection.ALL_RANDOM
            -1
            if config["max_number_of_variations_per_action"] is None
            else config["max_number_of_variations_per_action"]
        )

        store.settings.sa_strict_ordered = config["sa_solution_order"] == "greedy"
        store.settings.action_variation_selection = (
            config["action_variation_selection"]
            if store.settings.max_variants_per_action != -1
            else config["action_variation_selection"].infinite_max_variants
        )
        Settings.SHOW_SIMULATION_ERRORS = False
        Settings.RAISE_SIMULATION_ERRORS = False
        Settings.COST_TYPE = config["cost_type"]
        # We don't want to deal with the hastle of the global singleton solution dumper
        Settings.DUMP_DISCARDED_SOLUTIONS = False
        Settings.NUMBER_OF_CASES = config["num_cases"]
        Settings.ARCHIVE_TENSORBOARD_LOGS = False
        Settings.ARCHIVE_SOLUTIONS = False
        Settings.DELETE_LOADED_SOLUTION_ARCHIVES = False
        Settings.OVERWRITE_EXISTING_SOLUTION_ARCHIVES = False

        # Keep one cpu core free for other processes (e.g. web request handling)
        Settings.MAX_THREADS_ACTION_EVALUATION = max(1, (os.cpu_count() or 1) - 1)

        store.settings.optimos_legacy_mode = config["mode"] == "timetable"
        store.settings.batching_only = config["mode"] == "batching"

        # We limit the number of actions to select to the number of threads
        store.settings.max_number_of_actions_per_iteration = min(
            (config["max_actions_per_iteration"] or 1000), Settings.MAX_THREADS_ACTION_EVALUATION
        )
        store.settings.legacy_approach = (
            LegacyApproach.from_abbreviation(config["approach"])
            if config["approach"] is not None
            else LegacyApproach.CALENDAR_FIRST
        )
        store.settings.max_iterations = config["max_iterations"]
        store.settings.max_non_improving_actions = config["max_non_improving_actions"]
        store.settings.agent = config["agent"]

        # Upload initial evaluation
        self.iteration_callback(store)

        optimizer = Optimizer(store)
        generator = optimizer.get_iteration_generator()

        for _ in generator:
            if self.cancelled:
                print("Optimization Cancelled!")
                break

            self.iteration_callback(store)
        self.iteration_callback(
            store,
            last_iteration=True,
        )
        self.running = False

    def iteration_callback(self, store: Store, last_iteration=False):
        """Write Iteration to file."""
        try:
            json_solutions = JSONReport.from_store(store, is_final=last_iteration)
            json_content = json_solutions.model_dump_json()
            # Replace Infinity and NaN with their String representation

            with ZipFile(self.output_path, "w", compression=ZIP_DEFLATED) as zipf:
                zipf.writestr("result.json", json_content)
        except Exception as e:
            print(f"Error writing iteration callback: {e}")
            print(traceback.format_exc())
            raise e
