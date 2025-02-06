import json
import xml.etree.ElementTree as ET

import numpy as np

from o2.models.constraints import ConstraintsType, SizeRuleConstraints
from o2.models.solution import Solution
from o2.models.state import State
from o2.models.timetable import BATCH_TYPE, RULE_TYPE, TimetableType
from o2.store import Store


def calculate_hyperarea(
    solutions: list[Solution], center_point: tuple[float, float]
) -> float:
    """Calculate the hyperarea covered by a set of solutions relative to a center point."""
    total_area = 0.0
    for solution in solutions:
        x, y = solution.point
        area = (center_point[0] - x) * (center_point[1] - y)
        if area > 0:  # Ignore invalid solutions
            total_area += area
    return total_area


def distance(point1, point2):
    return float(np.linalg.norm(np.array(point1) - np.array(point2)))


def calculate_averaged_hausdorff_distance(
    pareto_front: list[Solution], global_set: list[Solution]
) -> float:
    """Calculate the Averaged Hausdorff Distance between the Pareto front and the global set."""
    total_distance = 0.0
    for solution in pareto_front:
        distances = [distance(solution.point, other.point) for other in global_set]
        total_distance += min(distances)

    # Average over the Pareto front size
    return total_distance / len(pareto_front) if pareto_front else 0.0


def calculate_delta_metric(
    pareto_front: list[Solution], global_set: list[Solution]
) -> float:
    """Calculate the Delta metric for diversity of the Pareto front."""
    if not pareto_front:
        return 0.0

    distances = [
        np.linalg.norm(np.array(p1.point) - np.array(p2.point))
        for i, p1 in enumerate(pareto_front)
        for j, p2 in enumerate(pareto_front)
        if i < j
    ]

    avg_distance = np.mean(distances) if distances else 0.0
    return float(np.std(distances) / avg_distance) if avg_distance > 0 else 0.0


def calculate_purity(pareto_front: list[Solution], global_set: list[Solution]) -> float:
    """Calculate the Purity metric for the Pareto front."""
    pareto_set = {tuple(sol.point) for sol in pareto_front}
    global_set_points = {tuple(sol.point) for sol in global_set}
    pure_points = pareto_set.intersection(global_set_points)
    return len(pure_points) / len(pareto_front) if pareto_front else 0.0


def store_from_files(
    timetable_path: str, constraints_path: str, bpmn_path: str
) -> Store:
    """Create a store from the given files."""
    with open(timetable_path) as f:
        timetable = TimetableType.from_dict(json.load(f))

    with open(constraints_path) as f:
        constraints = ConstraintsType.from_dict(json.load(f))

    with open(bpmn_path) as f:
        bpmn_definition = f.read()

    initial_state = State(
        bpmn_definition=bpmn_definition,
        timetable=timetable,
    )
    return Store.from_state_and_constraints(
        initial_state,
        constraints,
    )


def base_line_constraints(
    bpmn_path: str, duration_fn: str, cost_fn: str
) -> ConstraintsType:
    bpmn_root = ET.parse(bpmn_path)
    # Get all the Elements of kind bpmn:task in bpmn:process
    tasks = bpmn_root.findall(".//{http://www.omg.org/spec/BPMN/20100524/MODEL}task")
    task_ids = [task.attrib["id"] for task in tasks]
    constraints = ConstraintsType(
        batching_constraints=[
            SizeRuleConstraints(
                id=f"size_rule_{task_id}",
                tasks=[task_id],
                batch_type=BATCH_TYPE.PARALLEL,
                rule_type=RULE_TYPE.SIZE,
                duration_fn=duration_fn,
                cost_fn=cost_fn,
                min_size=1,
                max_size=10,
            )
            for task_id in task_ids
        ],
    )
    # TODO: Add more constraints
    return constraints


def store_with_baseline_constraints(
    timetable_path: str,
    bpmn_path: str,
    duration_fn: str,
    cost_fn: str,
) -> Store:
    """Create a store from the given files and constraints."""
    constraints = base_line_constraints(bpmn_path, duration_fn, cost_fn)
    with open(timetable_path) as f:
        timetable = TimetableType.from_dict(json.load(f))

    with open(bpmn_path) as f:
        bpmn_definition = f.read()

    initial_state = State(
        bpmn_definition=bpmn_definition,
        timetable=timetable,
    )
    return Store.from_state_and_constraints(
        initial_state,
        constraints,
    )
