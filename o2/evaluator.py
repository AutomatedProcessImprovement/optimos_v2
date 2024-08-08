from __future__ import annotations

# Ignore FutureWarnings
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

import io

import pandas as pd

from o2.models.evaluation import Evaluation
from o2.simulation_runner import Log


class Evaluator:
    @staticmethod
    def parse_stats(stats: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Parse the csv statistics to a dataframe."""
        resource_stats_csv = stats.split("Resource Utilization\r\n")[1].split('""\r\n')[
            0
        ]

        # Read the CSV data into a DataFrame. Columns for reference:
        # Resource ID,
        # Resource name,
        # Utilization Ratio,
        # Tasks Allocated,
        # Worked Time (seconds),
        # Available Time (seconds),
        # Pool ID,
        # Pool name
        resource_statistics_df = pd.read_csv(
            io.StringIO(resource_stats_csv),
            sep=",",
        )

        task_stats_csv = stats.split("Individual Task Statistics\r\n")[1].split(
            '""\r\n'
        )[0]

        # Read the CSV data into a DataFrame. Columns for reference:
        # Name,
        # Count,
        # Min Duration,
        # Max Duration,
        # Avg Duration,
        # Total Duration,
        # Min Waiting Time,
        # Max Waiting Time,
        # Avg Waiting Time,
        # Total Waiting Time,
        # Min Processing Time,
        # Max Processing Time,
        # Avg Processing Time,
        # Total Processing Time,
        # Min Cycle Time,
        # Max Cycle Time,
        # Avg Cycle Time,
        # Total Cycle Time,
        # Min Idle Time,
        # Max Idle Time,
        # Avg Idle Time,
        # Total Idle Time,
        # Min Idle Cycle Time,
        # Max Idle Cycle Time,
        # Avg Idle Cycle Time,
        # Total Idle Cycle Time,
        # Min Idle Processing Time,
        # Max Idle Processing Time,
        # Avg Idle Processing Time,
        # Total Idle Processing Time,
        # Min Cost,
        # Max Cost,
        # Avg Cost,
        # Total Cost
        task_statistics_df = pd.read_csv(
            io.StringIO(task_stats_csv),
            sep=",",
        )

        return task_statistics_df, resource_statistics_df

    @staticmethod
    def evaluate_log(log: Log, stats: str) -> Evaluation:
        """Evaluate the log and statistics to return an Evaluation object."""
        if len(log) == 0:
            return Evaluation.empty()

        task_statistics_df, resource_statistics = Evaluator.parse_stats(stats)

        # Calculate the accumulated total cycle time and total cost
        accumulated_total_cycle_time = task_statistics_df["Total Cycle Time"].sum()
        accumulated_total_cost = task_statistics_df["Total Cost"].sum()
        accumulated_waiting_time = task_statistics_df["Total Waiting Time"].sum()

        return Evaluation(
            task_statistics_df,
            resource_statistics,
            log,
            accumulated_total_cycle_time,
            accumulated_total_cost,
            accumulated_waiting_time,
        )

        # # build an interval for the log timeframe
        # log_timeframe = Interval(
        #     begin=min(event.start for event in log),
        #     end=max(event.end for event in log),
        # )
        # calendar = {
        #     resource: calendar.apply(log_timeframe)
        #     for (resource, calendar) in discover_calendars(tuple(log)).items()
        # }

        # log = discover_batches(log)

        # log = WaitingTimeCanvas.apply(log, calendar)

        # dataframe = pd.json_normalize([event.asdict() for event in log])

        # dataframe["wt_total"] = dataframe["waiting_time.total.duration_in_seconds"]
        # dataframe["wt_contention"] = dataframe[
        #     "waiting_time.contention.duration_in_seconds"
        # ]
        # dataframe["wt_batching"] = dataframe[
        #     "waiting_time.batching.duration_in_seconds"
        # ]
        # dataframe["wt_prioritization"] = dataframe[
        #     "waiting_time.prioritization.duration_in_seconds"
        # ]
        # # dataframe["wt_unavailability"] = dataframe[
        # #     "waiting_time.unavailability.duration_in_seconds"
        # # ]
        # dataframe["wt_extraneous"] = dataframe[
        #     "waiting_time.extraneous.duration_in_seconds"
        # ]

        # result_df = (
        #     dataframe.groupby(["activity"])
        #     .agg(
        #         {
        #             "wt_total": "sum",
        #             "wt_contention": "sum",
        #             "wt_batching": "sum",
        #             "wt_prioritization": "sum",
        #             # "wt_unavailability": "sum",
        #             "wt_extraneous": "sum",
        #         }
        #     )
        #     .reset_index()
        # )

        # return Evaluation()
