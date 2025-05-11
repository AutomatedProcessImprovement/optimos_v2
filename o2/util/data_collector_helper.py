import json
import xml.etree.ElementTree as ET
from typing import Optional

from o2.models.constraints import ConstraintsType, SizeRuleConstraints
from o2.models.state import State
from o2.models.timetable import BATCH_TYPE, RULE_TYPE, TimetableType
from o2.store import Store


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
