import {
  ActionIcon,
  Badge,
  Text,
  Box,
  Card,
  Group,
  LoadingOverlay,
  Stack,
} from "@mantine/core";
import React, { FC, useEffect, useState } from "react";
import { removeRunningOptimization } from "../redux/slices/uiStateSlice";
import { useDispatch } from "react-redux";

import {
  IconCancel,
  IconCircle,
  IconCircleCheck,
  IconExclamationCircle,
  IconHelpCircle,
  IconProgress,
  IconSquareCheck,
  IconTrash,
} from "@tabler/icons-react";
import { useNavigate } from "react-router-dom";
import {
  useCancelOptimizationCancelOptimizationIdPostMutation,
  useGetStatusStatusIdGetQuery,
} from "../redux/slices/optimosApi";

type OutputCardProps = {
  outputId: string;
};

export const OutputCard: FC<OutputCardProps> = ({ outputId }) => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const shortId = outputId.split("-")[0];
  const [pollingInterval, setPollingInterval] = useState(3000);
  const {
    data: status,
    isLoading: isStatusLoading,
    error,
  } = useGetStatusStatusIdGetQuery(
    { id: outputId },
    { pollingInterval: pollingInterval, skipPollingIfUnfocused: true }
  );

  useEffect(() => {
    if (status === "completed" || status === "cancelled") {
      setPollingInterval(0);
    }
  }, [status]);

  const [cancelRequest, { isLoading: isCancelLoading }] =
    useCancelOptimizationCancelOptimizationIdPostMutation();

  const notFound = error && "status" in error && error?.status === 404;

  const Icon = notFound
    ? IconHelpCircle
    : error
    ? IconExclamationCircle
    : status == "completed"
    ? IconCircleCheck
    : status == "cancelled"
    ? IconCancel
    : status == "running"
    ? IconProgress
    : IconSquareCheck;

  const iconColor =
    status == "completed"
      ? "green"
      : status == "cancelled"
      ? "red"
      : status == "running"
      ? "blue"
      : "gray";

  const statusText = notFound
    ? "Not found on Server"
    : error
    ? "Unknown Error"
    : status;

  return (
    <Card
      pos="relative"
      shadow="sm"
      padding="md"
      radius="md"
      style={{
        cursor: "pointer",
        transition: "border 0.2s ease",
      }}
      onClick={() => navigate(`/results/${outputId}`)}
    >
      <Group justify="space-between" align="center">
        <Group>
          <Icon size={24} color={iconColor} />
          <Stack gap={0}>
            <Text size="sm">Optimization {shortId}</Text>
            <Badge color={iconColor} size="xs">
              {statusText}
            </Badge>
          </Stack>
        </Group>
        {(status != "running" || notFound) && (
          <ActionIcon
            color={"gray"}
            onClick={(e) => {
              e.stopPropagation(); // Prevent the click from triggering the selection
              dispatch(removeRunningOptimization(outputId));
            }}
          >
            <IconTrash size={18} />
          </ActionIcon>
        )}
        {status == "running" && !notFound && (
          <ActionIcon
            color={iconColor}
            onClick={(e) => {
              e.stopPropagation(); // Prevent the click from triggering the selection
              cancelRequest({ id: outputId });
            }}
          >
            <IconCancel size={18} />
          </ActionIcon>
        )}
      </Group>
    </Card>
  );
};
