import type { FC } from "react";
import React, { useContext } from "react";
import * as Highcharts from "highcharts";
import { HighchartsReact } from "highcharts-react-official";

import { Grid } from "@mantine/core";
import { useNavigate } from "react-router-dom";
import { formatSeconds, formatCurrency } from "../../util/num_helper";
import { useInitialSolution } from "../../hooks/useInitialSolution";
import { JsonSolution } from "../../redux/slices/optimosApi";

interface SolutionChartProps {
  optimalSolutions: JsonSolution[];
  otherSolutions: JsonSolution[];
}

export const SolutionChart: FC<SolutionChartProps> = ({
  optimalSolutions,
  otherSolutions,
}) => {
  const navigate = useNavigate();
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
        return `<span style="text-transform: capitalize;text-decoration: underline;">${
          this.point.name
        }</span><br><b>Time:</b> ${formatSeconds(
          this.x as number
        )}<br><b>Cost:</b> ${formatCurrency(this.y ?? 0)}`;
      },
    },
    xAxis: {
      title: {
        text: "Time",
      },
      labels: {
        formatter: function () {
          return Math.round(((this.value as number) * 10) / 60 / 60) / 10 + "h";
        },
      },
    },
    yAxis: {
      title: {
        text: "Cost",
      },
      labels: {
        formatter: function () {
          return formatCurrency(this.value as number);
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
              if (this.color === "red")
                return navigate("#initial-solution-acc");
              if (this.color === "gray")
                return navigate("#non-optimal-solutions");
              // Navigate to specific execution via anchor link
              navigate(`#solution_${this.index}`);
            },
          },
        },
      },
    },
    series: [
      {
        name: "Other Solutions",
        data: otherSolutions.map((solution, index) => ({
          x: solution.global_info.total_time,
          y: solution.global_info.total_cost,
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
            x: initialSolution?.global_info.total_time,
            y: initialSolution?.global_info.total_cost,
            id: `execution_${0}`,
            name: `Solution #${initialSolution?.solution_no}`,
          },
        ],
        color: "red",
        type: "scatter",
      },
      {
        name: "Optimal Solution",
        data: optimalSolutions.map((solution, index) => ({
          x: solution.global_info.total_time,
          y: solution.global_info.total_cost,
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
