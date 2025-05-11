import json
import sys
import xml.etree.ElementTree as ElementTree

import memray

import o2.optimizer
import o2.store
from o2.models.constraints import ConstraintsType
from o2.models.settings import Settings
from o2.models.timetable import TimetableType


def main() -> None:
    # timetable_path = "examples/demo_batching/timetable.json"
    # constraints_path = "examples/demo_batching/constraints.json"
    # bpmn_path = "examples/demo_batching/model.bpmn"

    timetable_path = "examples/demo_legacy/timetable.json"
    constraints_path = "examples/demo_legacy/constraints.json"
    bpmn_path = "examples/demo_legacy/model.bpmn"

    # timetable_path = "examples/purchase_timetable.json"
    # constraints_path = "examples/purchase_constraints.json"
    # bpmn_path = "examples/purchase.bpmn"

    with open(timetable_path) as f:
        timetable = TimetableType.from_dict(json.load(f))

    with open(constraints_path) as f:
        constraints = ConstraintsType.from_dict(json.load(f))

    with open(bpmn_path) as f:
        bpmn_definition = f.read()

    initial_state = o2.store.State(
        bpmn_definition=bpmn_definition,
        timetable=timetable,
    )
    store = o2.store.Store.from_state_and_constraints(
        initial_state,
        constraints,
    )

    # Change settings here:
    # store.settings.[...] = ...

    # Enable legacy mode
    Settings.MAX_THREADS_ACTION_EVALUATION = 5
    Settings.DISABLE_PARALLEL_EVALUATION = True
    store.settings.optimos_legacy_mode = True
    store.settings.max_iterations = 10
    store.settings.max_number_of_actions_per_iteration = 5

    optimizer = o2.optimizer.Optimizer(store)
    optimizer.solve()


# SimulationRunner.run_simulation(store.state)


if __name__ == "__main__":
    # Memory Profiling
    with memray.Tracker("optimos_v2.bin"):
        main()

    # Uncomment for CPU Profiling
    # yappi.set_clock_type("WALL")
    # yappi.start()
    # main()
    # yappi.stop()
    # yappi.get_func_stats().print_all(
    #     columns={
    #         0: ("name", 80),
    #         1: ("ncall", 5),
    #         2: ("tsub", 8),
    #         3: ("ttot", 8),
    #         4: ("tavg", 8),
    #     }
    # )
    # threads = yappi.get_thread_stats()
    # for thread in threads:
    #     print(
    #         "Function stats for (%s) (%d)" % (thread.name, thread.id)
    #     )  # it is the Thread.__class__.__name__
    #     yappi.get_func_stats(ctx_id=thread.id).print_all(
    #         columns={
    #             0: ("name", 80),
    #             1: ("ncall", 5),
    #             2: ("tsub", 8),
    #             3: ("ttot", 8),
    #             4: ("tavg", 8),
    #         }
    #     )
