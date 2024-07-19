import csv
import io
import time
from typing import TYPE_CHECKING, Collection, TypeAlias

import pandas as pd
from bpdfr_simulation_engine.simulation_engine import run_simpy_simulation
from dynamik.input import EventMapping
from dynamik.input.csv import read_and_merge_csv_logs
from dynamik.model import Event
from wta import (
    WAITING_TIME_BATCHING_KEY,
    WAITING_TIME_TOTAL_KEY,
    EventLogIDs,
    add_enabled_timestamp,
    convert_timestamp_columns_to_datetime,
)

Log: TypeAlias = Collection[Event]

if TYPE_CHECKING:
    from o2.types.state import State


class SimulationRunner:
    @staticmethod
    def parse_log(logStringIO):
        # Override column names
        log_ids = EventLogIDs(
            case="case_id",
            activity="activity",
            start_time="start_time",
            end_time="end_time",
            enabled_time="enable_time",
            resource="resource",
        )
        # Reset the StringIO to read from the beginning
        logStringIO.seek(0)

        log = pd.read_csv(logStringIO)
        log = convert_timestamp_columns_to_datetime(log, log_ids, utc=True)

        duration_columns = [WAITING_TIME_TOTAL_KEY, WAITING_TIME_BATCHING_KEY]
        for column in duration_columns:
            if column in log.columns:
                log[column] = pd.to_timedelta(log[column])

        # discarding unnecessary columns
        log = log[
            [
                log_ids.case,
                log_ids.activity,
                log_ids.resource,
                log_ids.start_time,
                log_ids.end_time,
            ]
        ]

        # NOTE: sorting by end time is important for concurrency oracle that is run during batching analysis
        log.sort_values(
            by=[log_ids.end_time, log_ids.start_time, log_ids.activity], inplace=True
        )

        add_enabled_timestamp(log, log_ids)

        return log

    @staticmethod
    def run_simulation(state: "State") -> tuple[Log, str]:
        statsStringIO = io.StringIO()
        statsWriter = csv.writer(
            statsStringIO,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
        )

        logStringIO = io.StringIO()

        logWriter = csv.writer(
            logStringIO,
            delimiter=",",
            quotechar='"',
            quoting=csv.QUOTE_MINIMAL,
        )

        setup = state.to_sim_diff_setup()
        run_simpy_simulation(setup, statsWriter, logWriter)
        logStringIO.seek(0)

        with open(f"logs/log-{time.time()}.csv", "w") as f:
            f.write(logStringIO.getvalue())

        logStringIO.seek(0)
        statsStringIO.seek(0)
        log = list(
            read_and_merge_csv_logs(
                [logStringIO],  # type: ignore
                attribute_mapping=EventMapping(
                    start="start_time",
                    end="end_time",
                    enablement="enable_time",
                    case="case_id",
                    activity="activity",
                    resource="resource",
                ),
            )
        )

        return log, statsStringIO.read()
