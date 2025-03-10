import traceback
from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Optional, TypeAlias

from prosimos.simulation_engine import run_simpy_simulation
from prosimos.simulation_stats_calculator import (
    KPIMap,
    LogInfo,
    ResourceKPI,
)

from o2.models.settings import Settings
from o2.util.indented_printer import print_l3
from o2.util.logger import info

TaskKPIs: TypeAlias = dict[str, KPIMap]
RessourceKPIs: TypeAlias = dict[str, ResourceKPI]
SimulationKPIs: TypeAlias = tuple[KPIMap, TaskKPIs, RessourceKPIs, datetime, datetime]

RunSimulationResult: TypeAlias = tuple[KPIMap, TaskKPIs, RessourceKPIs, LogInfo]


if TYPE_CHECKING:
    from o2.models.state import State


@dataclass(frozen=True)
class MedianResult:
    """A result of a simulation run, to be used for median calculation."""

    total_cycle_time: float
    result: RunSimulationResult


class SimulationRunner:
    """Helper class to run simulations and return the results."""

    @staticmethod
    def run_simulation(state: "State") -> RunSimulationResult:
        """Run simulation and return the results."""
        try:
            setup = state.to_sim_diff_setup()
            result = run_simpy_simulation(setup, None, None)
            assert result is not None
            assert isinstance(result, tuple)

            simulation_kpis: SimulationKPIs = result[0]  # type: ignore
            log_info = result[1]
            (
                global_kpis,
                task_kpis,
                resource_kpis,
                _,
                _,
            ) = simulation_kpis

            return global_kpis, task_kpis, resource_kpis, log_info

        except Exception as e:
            print_l3(f"Error in simulation: {e}")
            if Settings.SHOW_SIMULATION_ERRORS:
                info(traceback.format_exc())
            raise e

    @staticmethod
    def run_simulation_median(state: "State") -> RunSimulationResult:
        """Run multiple simulations and return the median simulation's results."""
        results: list[MedianResult] = []
        for _ in range(Settings.NUMBER_OF_SIMULATION_FOR_MEDIAN):
            result = SimulationRunner.run_simulation(state)
            _, _, _, log_info = result

            first_enablement = min(
                [event.enabled_datetime for trace in log_info.trace_list for event in trace.event_list],
                default=log_info.started_at,
            )
            last_completion = max(
                [event.completed_datetime for trace in log_info.trace_list for event in trace.event_list],
                default=log_info.ended_at,
            )
            total_cycle_time = (last_completion - first_enablement).total_seconds()
            results.append(MedianResult(total_cycle_time, result))

        results.sort(key=lambda x: x.total_cycle_time)
        median_result = results[len(results) // 2]
        return median_result.result
