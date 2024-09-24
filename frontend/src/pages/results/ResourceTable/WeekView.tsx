import { Box, Grid, Text, Divider, Group } from "@mantine/core";
import React, { FC, useState, CSSProperties } from "react";
import { TimePeriod, WorkMasks } from "../../../redux/slices/optimosApi";

export type WeekViewProps = {
  entries: Record<string, TimePeriod[] | WorkMasks>;
  columnStyles: Record<string, CSSProperties>;
  columnIndices?: Record<string, number>;
};

export type InternalEntry = {
  day: string;
  hour: number;
  style?: CSSProperties;
  column: number;
};

const convertToInternalEntries = (
  entries: WeekViewProps["entries"],
  columnStyles: WeekViewProps["columnStyles"],
  columns: WeekViewProps["columnIndices"]
) => {
  const internalEntries: InternalEntry[] = [];
  for (const [name, timePeriods] of Object.entries(entries)) {
    if (Array.isArray(timePeriods)) {
      for (const timePeriod of timePeriods) {
        const day = timePeriod.from;
        const from = parseInt(timePeriod.beginTime.split(":")[0]);
        const to = parseInt(timePeriod.endTime.split(":")[0]);
        for (let hour = from; hour < to; hour++) {
          internalEntries.push({
            day,
            hour,
            style: columnStyles[name],
            column: columns?.[name] ?? 0,
          });
        }
      }
    } else {
      for (const [day, workMask] of Object.entries(timePeriods)) {
        workMask
          .toString(2)
          .padStart(24, "0")
          .split("")
          .forEach((value: string, index: number) => {
            if (value === "1") {
              internalEntries.push({
                day,
                hour: index,
                style: columnStyles[name],
                column: columns?.[name] ?? 0,
              });
            }
          });
      }
    }
  }
  return internalEntries;
};

export const WeekView: FC<WeekViewProps> = (props) => {
  const columnCount = Math.max(...Object.values(props.columnIndices ?? {}), 0);

  // Generate an array of 24 hours
  const hours = Array.from({ length: 24 }, (_, i) => i);

  // Generate an array of days starting from Monday to Sunday
  const days = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
  ];

  const internalEntries = convertToInternalEntries(
    props.entries,
    props.columnStyles,
    props.columnIndices
  );

  return (
    <Box>
      <Grid>
        <Grid.Col span={1} />

        {/* Days headers */}
        {days.map((day, index) => (
          <Grid.Col span="auto" key={index}>
            <Text ta="center" size="lg" fw={500}>
              {day}
            </Text>
          </Grid.Col>
        ))}
      </Grid>
      <Divider />
      <Grid>
        {/* Time column */}
        <Grid.Col span={1}>
          {hours.map((hour) => (
            <Box key={hour} style={{ textAlign: "center", height: 20 }}>
              <Text size="sm">{`${hour}:00`}</Text>
            </Box>
          ))}
        </Grid.Col>

        {/* Days events */}
        {days.map((day, dayIndex) => (
          <Grid.Col span="auto" key={dayIndex}>
            {hours.map((hour, hourIndex) => (
              <Group key={`hour-${day}-${hourIndex}`} gap={0}>
                {Array.from({ length: columnCount + 1 }, (_, i) => i).map(
                  (columnIndex) => {
                    const entry = internalEntries.find(
                      (entry) =>
                        entry.day.toLowerCase() === day.toLowerCase() &&
                        entry.hour === hour &&
                        entry.column === columnIndex
                    );
                    const hasEvent = entry !== undefined;

                    return (
                      <Box
                        key={`event-${day}-${hourIndex}-${columnIndex}`}
                        style={{
                          borderBottom: "1px solid",
                          borderColor: "rgb(142, 144, 144)",
                          flex: hasEvent ? 1 : 0,
                          ...(hasEvent ? entry?.style : {}),
                        }}
                        h={20}
                      />
                    );
                  }
                )}
              </Group>
            ))}
          </Grid.Col>
        ))}
      </Grid>
    </Box>
  );
};
