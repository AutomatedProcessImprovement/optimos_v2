import { Card, Grid, Text, Group } from "@mantine/core";
import type { FC } from "react";
import {
  IconCirclePlus,
  IconCopy,
  IconArrowRight,
  IconCircleMinus,
  IconTrash,
} from "@tabler/icons-react";
import React from "react";
import { JsonAction, JsonSolution } from "../../redux/slices/optimosApi";

type ModificationOverviewProps = {
  solution: JsonSolution;
};

export const ModificationOverview: FC<ModificationOverviewProps> = (props) => {
  const { solution } = props;
  const actions = solution.actions;

  return (
    <Grid>
      {actions.map((action, index) => {
        return (
          <Grid.Col span={{ md: 6, lg: 4, xl: 3 }} key={index}>
            <ActionCard action={action} />
          </Grid.Col>
        );
      })}
    </Grid>
  );
};

const ActionCard = ({ action }: { action: JsonAction }) => {
  let title;
  let description;
  let icon;

  switch (action.type) {
    case "AddResourceAction":
      icon = <IconCopy size={16} />;
      title = "Clone Resource";
      description = (
        <span>
          Cloned resource <b>{action.params["resource_id"]}.</b>
        </span>
      );
      break;
    case "ModifyCalendarByCostAction":
    case "ModifyCalendarByITAction":
    case "ModifyCalendarByWTAction":
      const resourceId = action.params["calendar_id"].replace("timetable", "");
      if ("shift_hours" in action.params) {
        icon = <IconArrowRight size={16} />;
        title = `Move shift to start${
          action.params["shift_hours"] > 0 ? " later" : " earlier"
        }`;
        description = (
          <span>
            Moved <b>shift "{action.params["period_id"]}"</b> on{" "}
            <b>{action.params["day"]}</b> by {action.params["shift_hours"]}{" "}
            hours for resource <b>{resourceId}</b>.
          </span>
        );
      } else if (
        "add_hours_after" in action.params &&
        "add_hours_before" in action.params
      ) {
        if (
          action.params["add_hours_after"] > 0 &&
          action.params["add_hours_before"] > 0
        ) {
          icon = <IconCirclePlus size={16} />;
          title = "Add hours before and after shift";
          description = (
            <span>
              Added {action.params["add_hours_before"]} hours before and{" "}
              {action.params["add_hours_after"]} hours after{" "}
              <b>shift "{action.params["period_id"]}"</b> on{" "}
              <b>{action.params["day"]}</b> for resource <b>{resourceId}</b>.
            </span>
          );
        } else if (
          action.params["add_hours_after"] < 0 &&
          action.params["add_hours_before"] < 0
        ) {
          icon = <IconCircleMinus size={16} />;
          title = "Remove hours before and after shift";
          description = (
            <span>
              Removed {Math.abs(action.params["add_hours_before"])} hours before
              and {Math.abs(action.params["add_hours_after"])} hours after{" "}
              <b>shift "{action.params["period_id"]}"</b> on{" "}
              <b>{action.params["day"]}</b> for resource <b>{resourceId}</b>.
            </span>
          );
        }
      } else if (
        "add_hours_after" in action.params &&
        action.params["add_hours_after"] > 0
      ) {
        icon = <IconCirclePlus size={16} />;
        title = "Add hours after shift";
        description = (
          <span>
            Added {action.params["add_hours_after"]} hours after{" "}
            <b>shift "{action.params["period_id"]}"</b> on{" "}
            <b>{action.params["day"]}</b> for resource <b>{resourceId}</b>.
          </span>
        );
      } else if (
        "add_hours_after" in action.params &&
        action.params["add_hours_after"] < 0
      ) {
        icon = <IconCircleMinus size={16} />;
        title = "Remove hours after shift";
        description = (
          <span>
            Removed {Math.abs(action.params["add_hours_after"])} hours after{" "}
            <b>shift "{action.params["period_id"]}"</b> on{" "}
            <b>{action.params["day"]}</b> for resource <b>{resourceId}</b>.
          </span>
        );
      } else if (
        "add_hours_before" in action.params &&
        action.params["add_hours_before"] > 0
      ) {
        icon = <IconCirclePlus size={16} />;
        title = "Add hours before shift";
        description = (
          <span>
            Added {action.params["add_hours_before"]} hours before{" "}
            <b>shift "{action.params["period_id"]}"</b> on{" "}
            <b>{action.params["day"]}</b> for resource <b>{resourceId}</b>.
          </span>
        );
      } else if (
        "add_hours_before" in action.params &&
        action.params["add_hours_before"] < 0
      ) {
        icon = <IconCircleMinus size={16} />;
        title = "Remove hours before shift";
        description = (
          <span>
            Removed {Math.abs(action.params["add_hours_before"])} hours before{" "}
            <b>shift "{action.params["period_id"]}"</b> on{" "}
            <b>{action.params["day"]}</b> for resource <b>{resourceId}</b>.
          </span>
        );
      } else if ("remove_period" in action.params) {
        icon = <IconTrash size={16} />;
        title = "Remove shift";
        description = (
          <span>
            Removed <b>shift "{action.params["period_id"]}"</b> on{" "}
            <b>{action.params["day"]}</b> for resource <b>{resourceId}</b>.
          </span>
        );
      }
      break;
    case "RemoveResourceByUtilizationAction":
      icon = <IconTrash size={16} />;
      title = "Remove Resource";
      description = (
        <span>
          Removed resource <b>{action.params["resource_id"]}.</b>
        </span>
      );
      break;
    default:
      console.warn("Unknown action type", action);
      title = "Unknown action";
      description = "Unknown action type";
  }

  return (
    <Card>
      <Group align="center" gap="xs" p="1rem">
        {icon}
        <Text size="lg" fw={500}>
          {title}
        </Text>
      </Group>
      <Text size="sm" px="1rem">
        {description}
      </Text>
    </Card>
  );
};
