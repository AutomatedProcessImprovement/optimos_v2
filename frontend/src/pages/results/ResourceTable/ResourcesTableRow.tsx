import {
  Table,
  Collapse,
  Box,
  Text,
  Grid,
  Chip,
  Button,
  Group,
  SimpleGrid,
} from "@mantine/core";
import { FC, useState } from "react";

import {
  IconChevronUp,
  IconChevronDown,
  IconCopy,
  IconAlertCircle,
  IconPlus,
  IconStatusChange,
  IconMinus,
  IconCircleMinus,
  IconChecklist,
  IconCirclePlus,
  IconReplace,
} from "@tabler/icons-react";
import { COLUMN_DEFINITIONS } from "./ResourcesTableColumnDefinitions";
import { ResourcesTableCell } from "./ResourcesTableCell";
import React from "react";
import { JsonResourceInfo, WorkMasks } from "../../../redux/slices/optimosApi";
import { WeekView } from "./WeekView";

type ResourceRowProps = {
  resource: JsonResourceInfo;
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
    modifiers: { deleted, added, tasks_modified, shifts_modified },
    assigned_tasks,
    removed_tasks,
    added_tasks,
    never_work_bitmask,
    always_work_bitmask,
  } = resource;

  const resource_calendar_entries = {
    neverWorkTimes: never_work_bitmask,
    alwaysWorkTimes: always_work_bitmask,
    ...getShifts(
      resource.original_timetable_bitmask,
      resource.timetable_bitmask
    ),
  };

  return (
    <>
      <Table.Tr>
        <Table.Td>
          <Button
            variant="subtle"
            size="compact-sm"
            onClick={() => setOpen(!open)}
          >
            {open ? <IconChevronUp size={16} /> : <IconChevronDown size={16} />}
          </Button>
        </Table.Td>
        <Table.Td>
          {deleted && (
            <Chip
              color="red"
              variant="outline"
              checked
              icon={<IconCircleMinus size={13} />}
            >
              Unused
            </Chip>
          )}
          {added && (
            <Chip
              icon={<IconCopy size={13} />}
              color="green"
              variant="outline"
              checked
            >
              New
            </Chip>
          )}
          {!added && !deleted && tasks_modified && (
            <Chip
              checked
              icon={<IconReplace size={13} />}
              color="yellow"
              variant="outline"
            >
              Tasks
            </Chip>
          )}
          {!added && !deleted && shifts_modified && (
            <Chip
              checked
              icon={<IconStatusChange size={13} />}
              color="yellow"
              variant="outline"
            >
              Shifts
            </Chip>
          )}
          {!deleted && !added && !tasks_modified && !shifts_modified && (
            <Chip color="gray" variant="outline" checked>
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
        {open && (
          <Table.Td colSpan={COLUMN_DEFINITIONS.length + 2}>
            <Text size="lg" fw={500} mb="xs">
              Assigned Tasks
            </Text>
            <SimpleGrid cols={2} maw={"550px"}>
              {assigned_tasks
                .filter(
                  (name) =>
                    !added_tasks?.includes(name) &&
                    !removed_tasks?.includes(name)
                )
                .map((name) => (
                  <Grid.Col key={name} span="auto">
                    <Chip
                      variant="outline"
                      checked
                      icon={<IconChecklist size={13} />}
                      color="black"
                    >
                      {name}
                    </Chip>
                  </Grid.Col>
                ))}
              {added_tasks.map((name) => (
                <Grid.Col key={name} span="auto">
                  <Chip
                    color="green"
                    variant="outline"
                    checked
                    icon={<IconCirclePlus size={13} />}
                  >
                    {name}
                  </Chip>
                </Grid.Col>
              ))}
              {removed_tasks?.map((name) => (
                <Grid.Col key={name} span="auto">
                  <Chip
                    color="red"
                    variant="outline"
                    checked
                    icon={<IconCircleMinus size={13} />}
                  >
                    {name}
                  </Chip>
                </Grid.Col>
              ))}
            </SimpleGrid>

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
                  borderBottom: "none",
                },
                alwaysWorkTimes: { backgroundColor: "lightblue" },
                onlyInOriginalShift: {
                  backgroundColor: "rgb(248,248,248)",
                  borderColor: "rgb(196,196,196)",
                  borderWidth: 1,
                  borderStyle: "dashed",
                  borderBottom: "none",
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

            <Group>
              <strong>Legend:</strong>
              <Box
                style={{
                  width: "10px",
                  height: "10px",
                  backgroundColor: "rgba(242, 107, 44, 0.5)",
                }}
              />
              Never Work Time
              <Box
                style={{
                  width: "10px",
                  height: "10px",
                  backgroundColor: "lightblue",
                }}
              />
              Always Work Time
              <Box
                style={{
                  width: "10px",
                  height: "10px",
                  backgroundColor: "darkgrey",
                }}
              />
              Unchanged Working Time
              <Box
                style={{
                  width: "10px",
                  height: "10px",
                  backgroundColor: "rgb(248,248,248)",
                  border: "1px dashed rgb(196,196,196)",
                }}
              />
              Removed Work Time
              <Box
                style={{
                  width: "10px",
                  height: "10px",
                  backgroundColor: "rgba(34,139,34, 0.7)",
                }}
              />
              Added Work Time
            </Group>
          </Table.Td>
        )}
      </Table.Tr>
    </>
  );
};
