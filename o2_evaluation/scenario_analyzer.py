import io
import json
import os
import time
from typing import TypedDict
from xml.etree import ElementTree

from o2.models.evaluation import Evaluation
from o2.models.state import State
from o2.models.timetable import TimetableType
from o2.simulation_runner import SimulationRunner
from o2_evaluation.data_collector import (
    store_with_baseline_constraints,
)


class ScenarioStats(TypedDict):
    scenario: str
    traces: int
    events: int
    activities: int
    resources: int
    arcs: int
    sim_time: float
    parallel_gateways: int
    exclusive_gateways: int
    inclusive_gateways: int


SCENARIOS = [
    "BPI_Challenge_2012",
    "BPI_Challenge_2017",
    "callcentre",
    "consulta_data_mining",
    "insurance",
    "production",
    "purchasing_example",
    "POC",
    "AC-CRD",
    "GOV",
    "WK-ORD",
    "BPIC2019_DAS",
    "Sepsis_DAS",
    "Trafic_DAS",
]


def get_activities_from_bpmn(bpmn_string: str) -> list[str]:
    """Get the activities from the BPMN file."""
    file_io = io.StringIO()
    file_io.write(bpmn_string)
    file_io.seek(0)
    bpmn = ElementTree.parse(file_io)
    bpmn_root = bpmn.getroot()
    # Get all the Elements of kind bpmn:task in bpmn:process
    tasks = bpmn_root.findall(".//{http://www.omg.org/spec/BPMN/20100524/MODEL}task")
    return [task.attrib["id"] for task in tasks]


def get_arcs_from_bpmn(bpmn_string: str) -> list[str]:
    """Get the arcs (<sequenceFlow />) from the BPMN file."""
    file_io = io.StringIO()
    file_io.write(bpmn_string)
    file_io.seek(0)
    bpmn = ElementTree.parse(file_io)
    bpmn_root = bpmn.getroot()
    arcs = bpmn_root.findall(
        ".//{http://www.omg.org/spec/BPMN/20100524/MODEL}sequenceFlow"
    )
    return [arc.attrib["id"] for arc in arcs]


def get_gateways_from_bpmn(bpmn_string: str) -> tuple[int, int, int]:
    """Get the gateways from the BPMN file."""
    file_io = io.StringIO()
    file_io.write(bpmn_string)
    file_io.seek(0)
    bpmn = ElementTree.parse(file_io)
    bpmn_root = bpmn.getroot()
    parallel_gateways = bpmn_root.findall(
        ".//{http://www.omg.org/spec/BPMN/20100524/MODEL}parallelGateway"
    )
    exclusive_gateways = bpmn_root.findall(
        ".//{http://www.omg.org/spec/BPMN/20100524/MODEL}exclusiveGateway"
    )
    inclusive_gateways = bpmn_root.findall(
        ".//{http://www.omg.org/spec/BPMN/20100524/MODEL}inclusiveGateway"
    )
    return len(parallel_gateways), len(exclusive_gateways), len(inclusive_gateways)


def get_scenario_stats(scenario: str) -> ScenarioStats:
    """Get the stats for a given scenario."""
    scenario_folder = "o2_evaluation/scenarios"
    if scenario == "Purchasing":
        timetable_path = f"{scenario_folder}/purchasing_example/purchasing_example.json"
        bpmn_path = f"{scenario_folder}/purchasing_example/purchasing_example.bpmn"
    else:
        timetable_path = f"{scenario_folder}/{scenario}/{scenario}.json"
        bpmn_path = f"{scenario_folder}/{scenario}/{scenario}.bpmn"
        # Check if the files exist
        if not os.path.exists(timetable_path):
            raise FileNotFoundError(
                f"Unknown scenario: {scenario}. Please check the scenario folder."
            )
        if not os.path.exists(bpmn_path):
            raise FileNotFoundError(
                f"Unknown scenario: {scenario}. Please check the scenario folder."
            )

    with open(timetable_path) as f:
        timetable = TimetableType.from_dict(json.load(f))

    with open(bpmn_path) as f:
        bpmn_definition = f.read()

    state = State(
        bpmn_definition=bpmn_definition,
        timetable=timetable,
    )

    setup = state.to_sim_diff_setup()
    result = SimulationRunner.run_simulation(state)

    global_kpis, task_kpis, resource_kpis, log_info = result

    events = sum(len(trace.event_list) for trace in log_info.trace_list)
    activities = len(get_activities_from_bpmn(bpmn_definition))
    resources = len(state.timetable.get_all_resources())
    arcs = len(get_arcs_from_bpmn(bpmn_definition))

    sim_time = 0
    print(f"Evaluating {scenario} 10 times...")
    for i in range(10):
        print(f"\t> Iteration {i + 1} of 10")
        start_time = time.time()
        state.evaluate()
        end_time = time.time()
        sim_time += end_time - start_time
    sim_time /= 10

    parallel_gateways, exclusive_gateways, inclusive_gateways = get_gateways_from_bpmn(
        bpmn_definition
    )

    return {
        "scenario": scenario,
        "traces": 1000,
        "events": events,
        "activities": activities,
        "resources": resources,
        "arcs": arcs,
        "parallel_gateways": parallel_gateways,
        "exclusive_gateways": exclusive_gateways,
        "inclusive_gateways": inclusive_gateways,
        "sim_time": sim_time,
    }


ROWS = [
    "traces",
    "events",
    "activities",
    "resources",
    "arcs",
    "parallel_gateways",
    "exclusive_gateways",
    "inclusive_gateways",
    "sim_time",
]
ROW_NAMES = [
    "Traces",
    "Events",
    "Activities",
    "Resources",
    "Arcs",
    "Parallel Gateways",
    "Exclusive Gateways",
    "Inclusive Gateways",
    "Simulation Time",
]

if __name__ == "__main__":
    stats: dict[str, ScenarioStats] = {}
    for scenario in SCENARIOS:
        print(f"Processing {scenario}...")
        stats[scenario] = get_scenario_stats(scenario)

    # Construct a Table with the stats as Rows and the scenarios as Columns
    result = ""
    # Title Case Scenario Names
    result += (
        f";{';'.join(scenario.replace('_', ' ').title() for scenario in SCENARIOS)}"
    )
    for row, row_name in zip(ROWS, ROW_NAMES):
        result += f"\n{row_name};{';'.join(str(stats[scenario][row]) for scenario in SCENARIOS)}"
    print(result.replace(".", ","))
