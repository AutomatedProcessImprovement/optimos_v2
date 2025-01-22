from collections import defaultdict
from datetime import datetime
from typing import TypedDict

from prosimos.simulation_stats_calculator import (
    LogInfo,
    TaskEvent,
)

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


def get_batches_from_event_log(
    log: LogInfo, batching_rules_exist=True
) -> dict[BatchInfoKey, BatchInfo]:
    """Identify batches with their key statistics.

    - wt_first: Time difference between enablement time of the first task in the batch to the starting time of the batch.
    - wt_last: Time difference between enablement time of the last task in the batch to the starting time of the batch.
    - real_proc:  real processing time of the batch, i.e., duration from start to end
    - ideal_proc: ideal processing time without considering idle time, i.e., removing the idle time from the real processing time.

    Additionally the activity, resource and start / end time are kept for each batch.
    """
    max_sequential_gap = 0

    batches: list[list[TaskEvent]] = []

    # Group events by resource and activity
    events_per_resource_and_activity: dict[
        tuple[str, str], list[TaskEvent]
    ] = defaultdict(list)

    events: list[TaskEvent] = [
        event for trace in log.trace_list for event in trace.event_list
    ]

    for event in events:
        if event.resource_id is not None:
            events_per_resource_and_activity[(event.resource_id, event.task_id)].append(
                event
            )

    # Build batches for each resource and activity
    for events in events_per_resource_and_activity.values():
        # Create a new empty batch (new activity implies new batch)
        current_batch: list[TaskEvent] = []
        current_start: float = float("inf")
        current_end: float = float("-inf")

        for event in sorted(events, key=lambda _evt: _evt.started_at or 0):
            if (
                event.enabled_at is None
                or event.started_at is None
                or event.completed_at is None
            ):
                continue
            # add event to current batch if in first iteration
            if len(current_batch) == 0:
                current_batch.append(event)
                current_start = event.started_at
                current_end = event.completed_at
            # add event to current batch if enabled between the first event enablement and the batch started executing
            elif (
                batching_rules_exist
                and event.enabled_at <= current_start
                and (event.started_at - current_end) <= max_sequential_gap
            ):
                current_batch.append(event)
                current_end = max(event.completed_at, current_end)
            # If the event is not part of the current batch, save the current batch and create a new one with the
            # current event
            else:
                batches.append(current_batch)
                current_batch = [event]
                current_start = event.started_at
                current_end = event.completed_at

        # Save the batch for the last iteration
        batches.append(current_batch)

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
        }

    return result
