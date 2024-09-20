import { Table, Collapse, Box, Text, Grid, Chip, Button } from "@mantine/core";
import { FC, useState } from "react";

import {
  IconChevronUp,
  IconChevronDown,
  IconCopy,
  IconAlertCircle,
  IconPlus,
} from "@tabler/icons-react"; // Replace with appropriate Mantine icons
import { COLUMN_DEFINITIONS } from "./ResourcesTableColumnDefinitions";
import { ResourcesTableCell } from "./ResourcesTableCell";
import React from "react";
import { WorkMasks } from "../../../redux/slices/optimosApi";
import { WeekView } from "./WeekView";
import { JSONResourceInfo } from "../../../types/optimos_json_type";

type ResourceRowProps = {
  resource: JSONResourceInfo;
};

const getShifts = (originalShift?: WorkMasks, currentShift?: WorkMasks) => {
  if (!originalShift || !currentShift) return undefined;
  const onlyInOriginalShift: WorkMasks = {
    ...originalShift,
  };
  const onlyInCurrent: WorkMasks = {
    ...currentShift,
  };
  const unchangedShift: WorkMasks = {
    ...currentShift,
  };
  const DAYS: (keyof WorkMasks)[] = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
  ];
  for (const day of DAYS) {
    onlyInOriginalShift[day] =
      (originalShift[day] as number) & ~(currentShift[day] as number);
    onlyInCurrent[day] =
      (currentShift[day] as number) & ~(originalShift[day] as number);
    unchangedShift[day] =
      (currentShift[day] as number) & (originalShift[day] as number);
  }
  return { onlyInOriginalShift, onlyInCurrent, unchangedShift };
};

export const ResourceTableRow: FC<ResourceRowProps> = ({ resource }) => {
  const [open, setOpen] = useState(false);

  const {
    modifiers: { deleted, added, tasksModified, shiftsModified },
    assignedTasks,
    removedTasks,
    addedTasks,
    neverWorkBitmask,
    alwaysWorkBitmask,
  } = resource;

  const resource_calendar_entries = {
    neverWorkTimes: neverWorkBitmask,
    alwaysWorkTimes: alwaysWorkBitmask,
    ...getShifts(resource.originalTimetableBitmask, resource.timetableBitmask),
  };

  return (
    <>
      <Table.Tr>
        <Table.Td>
          <Button variant="subtle" compact-sm onClick={() => setOpen(!open)}>
            {open ? <IconChevronUp size={16} /> : <IconChevronDown size={16} />}
          </Button>
        </Table.Td>
        <Table.Td>
          {deleted && (
            <Chip color="red" variant="outline">
              Unused
            </Chip>
          )}
          {added && (
            <Chip icon={<IconCopy size={16} />} color="green" variant="outline">
              New
            </Chip>
          )}
          {!added && !deleted && tasksModified && (
            <Chip
              icon={<IconAlertCircle size={16} />}
              color="yellow"
              variant="outline"
            >
              Tasks
            </Chip>
          )}
          {!added && !deleted && shiftsModified && (
            <Chip
              icon={<IconAlertCircle size={16} />}
              color="yellow"
              variant="outline"
            >
              Shifts
            </Chip>
          )}
          {!deleted && !added && !tasksModified && !shiftsModified && (
            <Chip color="gray" variant="outline">
              Required
            </Chip>
          )}
        </Table.Td>
        {COLUMN_DEFINITIONS.map((column) => (
          <ResourcesTableCell
            key={column.id}
            column={column}
            resource={resource}
          />
        ))}
      </Table.Tr>

      <Table.Tr>
        <Table.Td colSpan={12} style={{ padding: 0 }}>
          <Collapse in={open}>
            <Box mt="sm" p="md">
              <Text size="lg" fw={500} mb="xs">
                Assigned Tasks
              </Text>
              <Grid>
                {assignedTasks
                  .filter((name) => !addedTasks?.includes(name))
                  .map((name) => (
                    <Grid.Col key={name} span="auto">
                      <Chip variant="outline">{name}</Chip>
                    </Grid.Col>
                  ))}
                {addedTasks.map((name) => (
                  <Grid.Col key={name} span="auto">
                    <Chip color="green" variant="outline">
                      {name}
                    </Chip>
                  </Grid.Col>
                ))}
                {removedTasks?.map((name) => (
                  <Grid.Col key={name} span="auto">
                    <Chip color="red" variant="outline">
                      {name}
                    </Chip>
                  </Grid.Col>
                ))}
              </Grid>

              <Text size="lg" fw={500} mt="lg" mb="xs">
                Calendar
              </Text>
              <WeekView
                entries={resource_calendar_entries}
                columnStyles={{
                  unchangedShift: { backgroundColor: "darkgrey" },
                  neverWorkTimes: {
                    backgroundColor: "rgba(242, 107, 44, 0.5)",
                    borderColor: "rgb(242, 107, 44)",
                    borderWidth: 1,
                    borderStyle: "dashed",
                  },
                  alwaysWorkTimes: { backgroundColor: "lightblue" },
                  onlyInOriginalShift: {
                    backgroundColor: "rgb(248,248,248)",
                    borderColor: "rgb(196,196,196)",
                    borderWidth: 1,
                    borderStyle: "dashed",
                  },
                  onlyInCurrent: {
                    backgroundColor: "rgba(34,139,34, 0.7)",
                  },
                }}
                columnIndices={{
                  unchangedShift: 0,
                  neverWorkTimes: 1,
                  alwaysWorkTimes: 0,
                  onlyInOriginalShift: 2,
                  onlyInCurrent: 2,
                }}
              />
              <Text size="xs" mt="sm">
                <Grid>
                  <Grid.Col span={6}>
                    <strong>Legend:</strong>
                  </Grid.Col>
                  <Grid.Col
                    span={6}
                    style={{ color: "rgba(242, 107, 44, 0.5)" }}
                  >
                    Never Work Time
                  </Grid.Col>
                  <Grid.Col span={6} style={{ color: "lightblue" }}>
                    Always Work Time
                  </Grid.Col>
                  <Grid.Col span={6} style={{ color: "darkgrey" }}>
                    Unchanged Working Time
                  </Grid.Col>
                  <Grid.Col span={6} style={{ color: "rgb(248,248,248)" }}>
                    Removed Work Time
                  </Grid.Col>
                  <Grid.Col span={6} style={{ color: "rgba(34,139,34, 0.7)" }}>
                    Added Work Time
                  </Grid.Col>
                </Grid>
              </Text>
            </Box>
          </Collapse>
        </Table.Td>
      </Table.Tr>
    </>
  );
};
