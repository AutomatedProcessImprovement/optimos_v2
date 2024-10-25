import time

import pandas as pd
from bpdfr_simulation_engine.simulation_stats_calculator import (
    LogInfo,
    TaskEvent,
)
from dynamik.model import Event, Log
from dynamik.utils.model import TimeInterval
from dynamik.utils.pm.batching import discover_batches
from dynamik.utils.pm.waiting import WaitingTimeCanvas
from intervaltree import Interval, IntervalTree

from o2.util.indented_printer import print_l2


def add_waiting_times_to_event_log(log: LogInfo) -> pd.DataFrame:
    """Convert the log to a DataFrame and add waiting times."""
    start = time.time()
    events: Log = tuple(
        event_to_dynamik_event(event)
        for trace in log.trace_list
        for event in trace.event_list
    )

    events = discover_batches(events)
    result = []

    for event in events:
        if event.batch is not None:
            waiting_time_batching_seconds = TimeInterval(
                intervals=[
                    # The batching time for an event is the interval between it has been enabled and the batch accumulation is done
                    Interval(
                        begin=event.enabled,
                        end=event.batch.accumulation.end,
                    ),
                ],
            ).duration.seconds
        else:
            waiting_time_batching_seconds = 0
        result.append(
            {
                "case": event.case,
                "activity": event.activity,
                "resource": event.resource,
                "waiting_time_batching_seconds": waiting_time_batching_seconds,
            }
        )

    dataframe = pd.DataFrame(
        result,
        columns=["case", "activity", "resource", "waiting_time_batching_seconds"],
    )

    return dataframe


def event_to_dynamik_event(event: TaskEvent) -> Event:
    """Convert a TaskEvent to a dynamik Event."""
    return Event(
        case=event.p_case,
        activity=event.task_id,
        resource=event.resource_id,
        start=event.started_datetime,
        end=event.completed_datetime,
        enabled=event.enabled_datetime,
    )
