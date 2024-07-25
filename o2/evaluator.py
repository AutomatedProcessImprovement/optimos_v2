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
    def parse_stats(stats: str):
        global_stats = stats.split("Individual Task Statistics\r\n")[1].split('""\r\n')[
            0
        ]

        # Read the CSV data into a DataFrame
        df = pd.read_csv(
            io.StringIO(global_stats),
            sep=",",
        )

        # Calculate the accumulated total cycle time and total cost
        accumulated_total_cycle_time = df["Total Cycle Time"].sum()
        accumulated_total_cost = df["Total Cost"].sum()
        accumulated_waiting_time = df["Total Waiting Time"].sum()

        return Evaluation(
            df=df,
            total_cost=accumulated_total_cost,
            total_cycle_time=accumulated_total_cycle_time,
            total_waiting_time=accumulated_waiting_time,
        )

    @staticmethod
    def evaluateLog(log: Log, stats: str):
        if len(log) == 0:
            return Evaluation.empty()

        return Evaluator.parse_stats(stats)

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
