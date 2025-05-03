import type { FC } from "react";
import React, { useContext } from "react";
import * as Highcharts from "highcharts";
import { HighchartsReact } from "highcharts-react-official";

import { Grid } from "@mantine/core";
import { useNavigate } from "react-router-dom";
import {
  formatSeconds,
  formatCurrency,
  formatMilliseconds,
} from "../../util/num_helper";
import { useInitialSolution } from "../../hooks/useInitialSolution";
import { JsonSolution, CostType } from "../../redux/slices/optimosApi";

interface SolutionChartProps {
  optimalSolutions: JsonSolution[];
  otherSolutions: JsonSolution[];
  costType: CostType;
}

const getXValue = (solution: JsonSolution, costType: CostType): number => {
  switch (costType) {
    case CostType.FixedCost:
      return solution.global_info.total_fixed_cost;
    case CostType.ResourceCost:
      return solution.global_info.total_cost_for_available_time;
    case CostType.TotalCost:
      return solution.global_info.total_cost_for_worked_time;
    case CostType.WtPt:
      return solution.global_info.total_processing_time;
    case CostType.AvgWtPtPerTaskInstance:
      return solution.global_info.avg_batch_processing_time_per_task_instance;
    default:
      return solution.global_info.total_cost_for_worked_time;
  }
};

const getYValue = (solution: JsonSolution, costType: CostType): number => {
  switch (costType) {
    case CostType.WtPt:
      return (
        solution.global_info.total_waiting_time +
        solution.global_info.total_task_idle_time
      );
    case CostType.AvgWtPtPerTaskInstance:
      return solution.global_info.avg_idle_wt_per_task_instance;
    default:
      return solution.global_info.total_time;
  }
};

const getXAxisTitle = (costType: CostType): string => {
  switch (costType) {
    case CostType.WtPt:
      return "Processing Time";
    case CostType.FixedCost:
      return "Fixed Cost";
    case CostType.ResourceCost:
      return "Resource Cost";
    case CostType.TotalCost:
      return "Total Cost";
    case CostType.AvgWtPtPerTaskInstance:
      return "Batch Processing per Task";
    default:
      return "Total Cost";
  }
};

const getYAxisTitle = (costType: CostType): string => {
  switch (costType) {
    case CostType.WtPt:
      return "Waiting Time";
    case CostType.AvgWtPtPerTaskInstance:
      return "WT-Idle per Task";
    default:
      return "Total Duration";
  }
};

const formatValue = (value: number, costType: CostType): string => {
  switch (costType) {
    case CostType.FixedCost:
    case CostType.ResourceCost:
    case CostType.TotalCost:
      return formatCurrency(value);
    case CostType.WtPt:
    case CostType.AvgWtPtPerTaskInstance:
      return formatMilliseconds(value);
    default:
      return formatCurrency(value);
  }
};

export const SolutionChart: React.FC<SolutionChartProps> = ({
  optimalSolutions,
  otherSolutions,
  costType,
}) => {
  const initialSolution = useInitialSolution();
  const options: Highcharts.Options = {
    chart: {
      type: "scatter",
      events: {},
    },
    title: {
      text: "Solutions",
    },
    tooltip: {
      formatter: function () {
        const xLabel = getXAxisTitle(costType);
        const yLabel = getYAxisTitle(costType);
        return `<span style="text-transform: capitalize;text-decoration: underline;">${
          this.point.name
        }</span><br><b>${xLabel}:</b> ${formatValue(
          this.x as number,
          costType
        )}<br><b>${yLabel}:</b> ${formatValue(this.y as number, costType)}`;
      },
    },
    xAxis: {
      title: {
        text: getXAxisTitle(costType),
      },
      labels: {
        formatter: function () {
          return formatValue(Number(this.value), costType);
        },
      },
    },
    yAxis: {
      title: {
        text: getYAxisTitle(costType),
      },
      labels: {
        formatter: function () {
          return formatValue(Number(this.value), costType);
        },
      },
    },
    plotOptions: {
      scatter: {
        marker: {
          symbol: "circle",
        },
        cursor: "pointer",
        point: {
          events: {
            click: function () {
              console.log(this);
              let id;
              if (this.color === "gray" || this.color == "red")
                id = "non-optimal-solutions";
              else id = `solution_${this.name.split("#")?.[1]}`;
              document.getElementById(id)?.scrollIntoView({
                behavior: "smooth",
                block: "center",
                inline: "center",
              });
            },
          },
        },
      },
    },
    series: [
      {
        name: "Other Solutions",
        data: (otherSolutions || []).map((solution, index) => ({
          x: getXValue(solution, costType),
          y: getYValue(solution, costType),
          id: `execution_${optimalSolutions.length + index}`,
          name: `Solution #${solution.solution_no}`,
        })),
        color: "gray",
        type: "scatter",
      },
      {
        name: "Initial Solution",
        data: [
          {
            x: getXValue(initialSolution, costType),
            y: getYValue(initialSolution, costType),
            id: `execution_${0}`,
            name: `Solution #${initialSolution?.solution_no}`,
          },
        ],
        color: "red",
        type: "scatter",
      },
      {
        name: "Optimal Solutions",
        data: (optimalSolutions || []).map((solution, index) => ({
          x: getXValue(solution, costType),
          y: getYValue(solution, costType),
          id: `execution_${index}`,
          name: `Solution #${solution.solution_no}`,
        })),
        type: "scatter",
      },
      // {
      //   name: "Average Solution",
      //   data: [
      //     {
      //       x: averageCost,
      //       y: averageTime,
      //     },
      //   ],
      //   type: "scatter",
      // },
    ],
  };

  return (
    <Grid.Col span={12}>
      <HighchartsReact highcharts={Highcharts} options={options} />
    </Grid.Col>
  );
};
