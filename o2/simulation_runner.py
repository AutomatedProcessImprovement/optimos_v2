import traceback
from datetime import datetime
from typing import TYPE_CHECKING, Collection, TypeAlias

import pandas as pd
from bpdfr_simulation_engine.simulation_engine import run_simpy_simulation
from bpdfr_simulation_engine.simulation_stats_calculator import (
    KPIMap,
    LogInfo,
    ResourceKPI,
)
from dynamik.model import Event
from wta import (
    WAITING_TIME_BATCHING_KEY,
    WAITING_TIME_TOTAL_KEY,
    EventLogIDs,
    add_enabled_timestamp,
    convert_timestamp_columns_to_datetime,
)

TaskKPIs: TypeAlias = dict[str, KPIMap]
RessourceKPIs: TypeAlias = dict[str, ResourceKPI]
SimulationKPIs: TypeAlias = tuple[KPIMap, TaskKPIs, RessourceKPIs, datetime, datetime]

RunSimulationResult: TypeAlias = tuple[KPIMap, TaskKPIs, RessourceKPIs, LogInfo]

Log: TypeAlias = Collection[Event]

if TYPE_CHECKING:
    from o2.models.state import State


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
    def run_simulation(
        state: "State",
        show_simulation_errors: bool = False,
    ) -> RunSimulationResult:
        """Run simulation and return the results."""
        try:
            setup = state.to_sim_diff_setup()
            result = run_simpy_simulation(setup, None, None)
            assert result is not None

            simulation_kpis: SimulationKPIs = result[0]  # type: ignore
            log_info = result[1]
            global_kpis, task_kpis, resource_kpis, start_time, end_time = (
                simulation_kpis
            )

            return global_kpis, task_kpis, resource_kpis, log_info
        except Exception as e:
            print(f"Error in simulation: {e}")
            if show_simulation_errors:
                print(traceback.format_exc())
            raise e
