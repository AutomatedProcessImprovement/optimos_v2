import {
  ActionIcon,
  Badge,
  Text,
  Box,
  Card,
  Group,
  LoadingOverlay,
} from "@mantine/core";
import React, { FC } from "react";
import { removeRunningOptimization } from "../redux/slices/uiStateSlice";
import { useDispatch } from "react-redux";
import { useGetStatusStatusIdGetQuery } from "../redux/slices/optimosApi";
import { IconTrash } from "@tabler/icons-react";

type OutputCardProps = {
  outputId: string;
};

export const OutputCard: FC<OutputCardProps> = ({ outputId }) => {
  const dispatch = useDispatch();
  const {
    data: status,
    isLoading,
    error,
  } = useGetStatusStatusIdGetQuery({ id: outputId });
  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.toString()}</div>;
  return (
    <Box pos="relative">
      <LoadingOverlay
        visible={isLoading}
        zIndex={1000}
        overlayProps={{ radius: "sm", blur: 2 }}
      />
      <Card
        shadow="sm"
        padding="md"
        radius="md"
        style={{
          cursor: "pointer",
          transition: "border 0.2s ease",
        }}
      >
        <Group justify="space-between" align="center">
          <Group>
            <div>
              <Text size="sm">{outputId}</Text>
              <Badge color="gray" size="xs">
                {outputId}
              </Badge>
            </div>
          </Group>
          <ActionIcon
            color="red"
            onClick={(e) => {
              e.stopPropagation(); // Prevent the click from triggering the selection
              dispatch(removeRunningOptimization(outputId));
            }}
          >
            <IconTrash size={18} />
          </ActionIcon>
        </Group>
      </Card>
    </Box>
  );
};
