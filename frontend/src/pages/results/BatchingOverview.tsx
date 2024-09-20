import React from "react";
import { Grid, Text } from "@mantine/core";
import { useInitialSolution } from "../../hooks/useInitialSolution";

import { formatSeconds } from "../../util/num_helper";
import { DiffInfo } from "./ResourceTable/ResourcesTableCell";

export const BatchingOverview = ({ solution }: { solution: JSONSolution }) => {
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
          {formatSeconds(solution.globalInfo.totalCost)}{" "}
          <DiffInfo
            a={initialSolution?.globalInfo.totalCost}
            b={solution.globalInfo.totalCost}
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
