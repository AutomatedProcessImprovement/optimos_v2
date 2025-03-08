import json
import math
import xml.etree.ElementTree as ET
from typing import Optional

import numpy as np

from o2.models.constraints import ConstraintsType, SizeRuleConstraints
from o2.models.solution import Solution
from o2.models.state import State
from o2.models.timetable import BATCH_TYPE, RULE_TYPE, TimetableType
from o2.store import Store


def distance(point1: tuple[float, float], point2: tuple[float, float]) -> float:
    """Calculate the Euclidean distance between two points."""
    return float(np.linalg.norm(np.array(point1) - np.array(point2)))


def calculate_hyperarea(pareto_solutions: list[Solution], reference_point: tuple[float, float]) -> float:
    """Compute the hyperarea of the Pareto solutions.

    The hyperarea is the hypervolume in 2D of the region dominated by the set of
    solutions and bounded above by the given reference_point.  Formally:

        HV(Y; r) = LebesgueMeasure(  ∪_{y ∈ Y}  [y, r]  )

    where each y ∈ Y is a 2D point, and r = (r_x, r_y) is "worse" than all y.

    NOTE: We are using a simplified version of the hyperarea calculation, which
    will only work will valid pareto fronts (e.g. no dominating solutions).
    """
    # Quick exit if there are no solutions
    if not pareto_solutions:
        return 0.0

    # Sort solutions in descending order by their x-coordinate
    sorted_solutions = sorted(pareto_solutions, key=lambda s: s.pareto_x, reverse=True)

    ref_x, ref_y = reference_point

    # Accumulate area by "slicing" from right to left
    area = 0.0
    # Start from the reference corner
    last_x = ref_x

    # Traverse from the solution with the largest x to the smallest
    for sol in sorted_solutions:
        x, y = sol.point

        width = last_x - x
        height = ref_y - y
        # Add the area of that rectangle
        area += width * height

        # Move the x-boundary left
        last_x = x

    return area


def generational_distance_p2(A: list[Solution], B: list[Solution]) -> float:
    """Compute GD₂(A,B).

    Steps:
    - For each solution a in A, find the minimum Euclidean distance to any b in B.
    - Accumulate the square of that minimum distance.
    - Return the square root of the average of those squared distances (RMS).
    """
    if not A:
        return 0.0
    sum_of_squares = 0.0
    for sol_a in A:
        a_pt = sol_a.point
        min_d = float("inf")
        for sol_b in B:
            b_pt = sol_b.point
            dist = distance(a_pt, b_pt)
            if dist < min_d:
                min_d = dist
        sum_of_squares += min_d**2

    mean_sq = sum_of_squares / len(A)
    return math.sqrt(mean_sq)


def calculate_averaged_hausdorff_distance(
    pareto_front: list[Solution], reference_set: list[Solution]
) -> float:
    """Calculate the p=2 averaged Hausdorff distance between two sets of solutions.

    The p=2 averaged Hausdorff distance (also called the modified Hausdorff distance)
    is defined as:

        Δ₂(A, B) = max{ GD₂(A, B), GD₂(B, A) },

    where GD₂(A, B) is the generational distance in the direction A->B:

        GD₂(A, B) = sqrt( (1/|A|) * Σ ( min_{b ∈ B} d(a,b) )² ), for a ∈ A.

    Here, d(a,b) is the usual Euclidean distance between points a and b.
    """
    if not pareto_front:
        return 0.0

    # Compute generational distance A->B and B->A
    gd_2 = generational_distance_p2(pareto_front, reference_set)
    igd_2 = generational_distance_p2(reference_set, pareto_front)

    # The averaged Hausdorff distance is the max of the two directions
    return max(gd_2, igd_2)


def calculate_delta_metric(pareto_front: list, reference_set: list) -> float:
    """Calculate the Delta metric for diversity of the Pareto front.

    Formel Definition:
        Δ = (d_f + d_l + sum(|d_i - d̄|)) / (d_f + d_l + (N - 1)*d̄)
    where:
      - d_f = distance(first Pareto solution, reference extreme)
      - d_l = distance(last Pareto solution, reference extreme)
      - d_i = distance between consecutive solutions (i and i+1)
      - d̄  = average of all d_i
      - N   = number of solutions in the Pareto front
    """
    # Handle edge case: no solutions
    if not pareto_front:
        return 0.0

    # 1. Determine "extreme" reference points from the reference set
    extreme_x = min(reference_set, key=lambda s: s.pareto_x)
    extreme_y = min(reference_set, key=lambda s: s.pareto_y)

    # 2. Sort the Pareto front along the same objective
    sorted_front_x = sorted(pareto_front, key=lambda s: s.pareto_x)
    sorted_front_y = sorted(pareto_front, key=lambda s: s.pareto_y)

    # If there is only 1 solution, there's no "spread"
    if len(sorted_front_x) == 1:
        # You might define Δ = 0 if only one solution is present.
        return 0.0

    # 3. Compute the distances according to the formula
    # d_f: distance between the first Pareto solution and the reference min
    d_f = distance(sorted_front_x[0].point, extreme_x.point)
    # d_l: distance between the last Pareto solution and the reference max
    d_l = distance(sorted_front_y[0].point, extreme_y.point)

    # d_i: consecutive distances between solutions in the sorted Pareto front
    # We just go one "direction" (x), because euclidean distance is commutative
    consecutive_d = []
    for i in range(1, len(sorted_front_x)):
        d_i = distance(sorted_front_x[i - 1].point, sorted_front_x[i].point)
        consecutive_d.append(d_i)

    # Average gap d̄
    d_bar = sum(consecutive_d) / len(consecutive_d)

    # Sum of absolute deviations from the mean gap
    sum_abs_dev = sum(abs(d_i - d_bar) for d_i in consecutive_d)

    # Numerator and denominator of the Delta formula
    numerator = d_f + d_l + sum_abs_dev
    denominator = d_f + d_l + (len(consecutive_d) * d_bar)

    if denominator == 0.0:
        return float("inf")

    delta = numerator / denominator
    return delta


def calculate_purity(pareto_front: list[Solution], reference_set: list[Solution]) -> float:
    """Calculate the Purity metric for the Pareto front."""
    pareto_set = {tuple(sol.point) for sol in pareto_front}
    reference_set_points = {tuple(sol.point) for sol in reference_set}
    pure_points = pareto_set.intersection(reference_set_points)
    return len(pure_points) / len(pareto_front) if pareto_front else 0.0


def store_from_files(timetable_path: str, constraints_path: str, bpmn_path: str) -> Store:
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
    bpmn_path: str, duration_fn: str, cost_fn: str, max_batch_size: int = 100
) -> ConstraintsType:
    """Create some baseline constraints."""
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
                max_size=max_batch_size,
            )
            for task_id in task_ids
        ],
    )
    return constraints


def store_with_baseline_constraints(
    timetable_path: str,
    bpmn_path: str,
    duration_fn: str,
    cost_fn: str,
    max_batch_size: int = 100,
    name: Optional[str] = None,
) -> Store:
    """Create a store from the given files and constraints."""
    constraints = base_line_constraints(bpmn_path, duration_fn, cost_fn, max_batch_size)
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
        name=name or "An Optimos Run",
    )
