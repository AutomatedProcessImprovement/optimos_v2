import { useSelector } from "react-redux";
import { selectRunningOptimizations } from "../redux/selectors/uiStateSelectors";
import { Box, Divider, Stack, Text } from "@mantine/core";
import React from "react";
import { OutputCard } from "./OutputCard";

export const OutputView = () => {
  const runningOPsIds = useSelector(selectRunningOptimizations);

  return (
    <Stack gap="xs">
      <Text size="lg" fw={500}>
        Outputs
      </Text>

      {runningOPsIds.map((id) => (
        <OutputCard key={id} outputId={id} />
      ))}
    </Stack>
  );
};
