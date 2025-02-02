import traceback
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

TaskKPIs: TypeAlias = dict[str, KPIMap]
RessourceKPIs: TypeAlias = dict[str, ResourceKPI]
SimulationKPIs: TypeAlias = tuple[KPIMap, TaskKPIs, RessourceKPIs, datetime, datetime]

RunSimulationResult: TypeAlias = tuple[KPIMap, TaskKPIs, RessourceKPIs, LogInfo]


if TYPE_CHECKING:
    from o2.models.state import State


class SimulationRunner:
    @staticmethod
    def run_simulation(state: "State") -> RunSimulationResult:
        """Run simulation and return the results."""
        try:
            setup = state.to_sim_diff_setup()
            result = run_simpy_simulation(setup, None, None)
            assert result is not None

            simulation_kpis: SimulationKPIs = result[0]  # type: ignore
            log_info = result[1]
            (
                global_kpis,
                task_kpis,
                resource_kpis,
                start_time,
                end_time,
            ) = simulation_kpis

            return global_kpis, task_kpis, resource_kpis, log_info
        except Exception as e:
            print_l3(f"Error in simulation: {e}")
            if Settings.SHOW_SIMULATION_ERRORS:
                print(traceback.format_exc())
            raise e
