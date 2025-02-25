from collections import defaultdict
from datetime import datetime
from typing import Callable, TypedDict

from prosimos.simulation_stats_calculator import (
    LogInfo,
    TaskEvent,
)

from o2.util.helper import lambdify_dict

BatchInfoKey = tuple[str, str, datetime]
"""Activity, resource, start time"""


class BatchInfo(TypedDict):
    """Batch information."""

    activity: str
    resource: str
    case: int
    start: datetime
    """Starting time of the batch execution"""
    end: datetime
    """Ending time of the batch execution"""
    accumulation_begin: datetime
    """Time when the first task in the batch was enabled"""
    accumulation_end: datetime
    """Time when the last task in the batch was enabled"""
    wt_first: float
    """Time difference between enablement time of the first task in the batch to the
      starting time of the batch."""
    wt_last: float
    """Sum of the difference between enablement of the last task and the starting
      time of the batch."""
    wt_total: float
    """Sum of the difference between enablement of each task and the starting time of
    the batch."""
    wt_batching: float
    """Sum of the difference between enablement of each task and the last enablement of
      the batch."""
    idle_time: float
    """Idle time of the batch"""
    real_proc: float
    """Real processing time of the batch, i.e., processing + idle time"""
    ideal_proc: float
    """Ideal processing time without considering idle time, i.e., removing the idle
      time from the real processing"""
    size: int
    """Number of tasks in the batch"""
    fixed_cost: float
    """Fixed cost of the batch"""


class SimpleBatchInfo(TypedDict):
    """Batch information."""

    accumulation_begin: datetime
    start: datetime
    ideal_proc: float
    idle_time: float


def get_batches_from_event_log(
    log: LogInfo,
    fixed_cost_fns: dict[str, Callable[[float], float]],
    batching_rules_exist=True,
) -> dict[BatchInfoKey, BatchInfo]:
    """Identify batches with their key statistics.

    - wt_first: Time difference between enablement time of the first task in the batch to the starting time of the batch.
    - wt_last: Time difference between enablement time of the last task in the batch to the starting time of the batch.
    - real_proc:  real processing time of the batch, i.e., duration from start to end
    - ideal_proc: ideal processing time without considering idle time, i.e., removing the idle time from the real processing time.

    Additionally the activity, resource and start / end time are kept for each batch.
    """
    batches: list[list[TaskEvent]] = []

    events: list[TaskEvent] = [
        event for trace in log.trace_list for event in trace.event_list
    ]

    # Group events by batch_id
    batches_dict: dict[str, list[TaskEvent]] = defaultdict(list)
    for event in events:
        if event.resource_id is not None and event.batch_id is not None:
            batches_dict[event.batch_id].append(event)
        else:
            # TODO: Be a bit smarter here and don't add unbatched events to the batches
            batches_dict[
                f"{event.p_case}_{event.task_id}_{event.resource_id}_{event.started_datetime}"
            ].append(event)

    # Convert to list of batches
    batches = list(batches_dict.values())

    result: dict[BatchInfoKey, BatchInfo] = {}

    for batch in batches:
        case = batch[0].p_case
        activity = batch[0].task_id
        resource = batch[0].resource_id
        execution_start: datetime = min([event.started_datetime for event in batch])
        execution_end: datetime = max([event.completed_datetime for event in batch])
        accumulation_begin: datetime = min(
            [
                event.enabled_datetime
                for event in batch
                if event.enabled_datetime is not None
            ]
        )
        accumulation_end: datetime = max(
            [
                event.enabled_datetime
                for event in batch
                if event.enabled_datetime is not None
            ]
        )
        if (activity, resource, execution_start) in result:
            continue
        batch_idle_time = batch[0].idle_time or 0
        processing_time = batch[0].idle_processing_time or 0
        ideal_processing_time = processing_time - batch_idle_time
        wt_total = sum(
            [
                (event.started_datetime - event.enabled_datetime).total_seconds()
                for event in batch
            ]
        )
        wt_batching = sum(
            [
                (accumulation_end - event.enabled_datetime).total_seconds()
                for event in batch
                if event.enabled_datetime is not None
            ]
        )

        fixed_cost = fixed_cost_fns.get(activity, lambda _: 0)(len(batch))

        result[(activity, resource, execution_start)] = {
            "case": case,
            "activity": activity,
            "resource": resource,
            "start": execution_start,
            "end": execution_end,
            "accumulation_begin": accumulation_begin,
            "accumulation_end": accumulation_end,
            "wt_first": (execution_start - accumulation_begin).seconds,
            "wt_last": (execution_start - accumulation_end).seconds,
            "wt_total": wt_total,
            "wt_batching": wt_batching,
            "idle_time": batch_idle_time,
            "real_proc": processing_time,
            "ideal_proc": ideal_processing_time,
            "size": len(batch),
            "fixed_cost": fixed_cost,
        }

    return result
