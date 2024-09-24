import React from "react";
import { Grid, Text } from "@mantine/core";
import { useInitialSolution } from "../../hooks/useInitialSolution";

import { formatSeconds } from "../../util/num_helper";
import { JsonSolution } from "../../redux/slices/optimosApi";
import { DiffInfo } from "./ResourceTable/DiffInfo";

export const BatchingOverview = ({ solution }: { solution: JsonSolution }) => {
  const initialSolution = useInitialSolution();

  return (
    <Grid>
      <Grid.Col span={5}>
        <Text fw={700} ta="left">
          Waiting time due to batching
        </Text>
        <Text fw={700} ta="left">
          Batching Changes
        </Text>
      </Grid.Col>
      <Grid.Col span={7}>
        <Text ta="left">
          {formatSeconds(solution.global_info.total_cost)}{" "}
          <DiffInfo
            a={initialSolution?.global_info.total_cost}
            b={solution.global_info.total_cost}
            formatFn={formatSeconds}
            lowerIsBetter
            suffix="initial solution"
            onlyShowDiff
            margin={0.0}
          />
        </Text>
      </Grid.Col>
    </Grid>
  );
};
