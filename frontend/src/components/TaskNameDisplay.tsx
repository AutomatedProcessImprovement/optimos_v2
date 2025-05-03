import React from "react";
import { Text, Tooltip } from "@mantine/core";
import { useTaskNames } from "../hooks/useTaskNames";

type TaskNameDisplayProps = {
  taskId: string;
};

export const TaskNameDisplay: React.FC<TaskNameDisplayProps> = ({ taskId }) => {
  const taskNames = useTaskNames();
  const taskName = taskNames[taskId] ?? taskId;

  return (
    <Tooltip
      label={`Activity ID: ${taskId}`}
      withArrow
      position="top"
      transitionProps={{ transition: "fade", duration: 200 }}
    >
      <Text
        component="span"
        style={{
          borderBottom: "1px dashed var(--mantine-color-gray-4)",
          cursor: "help",
        }}
      >
        {taskName}
      </Text>
    </Tooltip>
  );
};
