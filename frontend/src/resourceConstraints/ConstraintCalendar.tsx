import { Grid, Box, Text, Divider, useMantineTheme } from "@mantine/core";
import type { FC } from "react";
import { useRef, useEffect } from "react";
import Selecto from "react-selecto";

import {
  DAYS,
  HOURS,
  bitmaskToSelectionIndexes,
  isTimePeriodInDay,
  isTimePeriodInHour,
} from "../helpers";

import {
  useSimParamsResourceIndex,
  useSimParamsWorkTimes,
} from "../hooks/useSimParamsWorkTimes";
import React from "react";
import { ConstraintWorkMask } from "../types/optimos_json_type";
import { useMasterFormContext } from "../hooks/useFormContext";
import { useFormError } from "../hooks/useFormError";

type ConstraintCalendarProps = {
  field: "never_work_masks" | "always_work_masks";
  color: string;
  resourceId: string;
  onSelectChange: (selection: Array<HTMLElement | SVGElement>) => void;
};

export const ConstraintCalendar: FC<ConstraintCalendarProps> = ({
  field,
  onSelectChange,
  color,
  resourceId,
}) => {
  const selectoRef = useRef<Selecto | null>(null);
  const form = useMasterFormContext();
  const containerClassName = `${field}-container`;

  const resources = form.values?.constraints?.resources;
  const workMask = resources.find((resource) => resource.id === resourceId)
    ?.constraints[field] as ConstraintWorkMask;

  useEffect(() => {
    // Finds the selected element by data-column, data-day, and data-index
    const targets = document.querySelectorAll<HTMLElement>(
      `.${containerClassName} .element`
    );
    const selectedTargets = Array.from(targets.values()).filter((element) => {
      const index = parseInt(element.dataset.index!);
      const day = element.dataset.day as (typeof DAYS)[number];
      return (workMask?.[day] ?? 0) & (1 << (23 - index));
    });
    selectoRef.current?.setSelectedTargets(selectedTargets);
  }, [containerClassName, workMask]);

  const theme = useMantineTheme();

  return (
    <Box className={containerClassName}>
      <Selecto
        ref={selectoRef}
        dragContainer={`.${containerClassName}`}
        selectableTargets={[`.${containerClassName} .element`]}
        hitRate={0}
        selectFromInside={true}
        selectByClick={true}
        continueSelect={true}
        onSelect={(e) => onSelectChange(e.selected)}
      />
      <Box>
        <Grid gutter={0}>
          <Grid.Col span={1.5} />

          {/* Days headers */}
          {DAYS.map((day, index) => (
            <Grid.Col span={1.5} key={index}>
              <Text ta="center" fw={500} tt="capitalize">
                {day}
              </Text>
            </Grid.Col>
          ))}
          <Grid.Col span={7 * 1.5} offset={1.5}>
            <Divider />
          </Grid.Col>
          {/* Time column */}
          <Grid.Col span={1.5} ta="right">
            {HOURS.map((hour) => (
              <Grid
                key={`hour-label-${hour}`}
                style={{
                  height: 30,
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                  borderColor: theme.colors["gray"][5],

                  borderRightWidth: "1px",
                  borderRightStyle: "solid",
                }}
              >
                <Text size="sm">{`${hour}:00`}</Text>
              </Grid>
            ))}
          </Grid.Col>

          {DAYS.map((day, dayIndex) => (
            <Grid.Col span={1.5}>
              <ConstraintDay
                color={color}
                key={`constraint-day-${day}`}
                day={day}
                field={field}
                resourceId={resourceId}
                workMask={workMask[day]}
              />
            </Grid.Col>
          ))}
        </Grid>
      </Box>
      <Text
        size="xs"
        color="dimmed"
        style={{ display: "flex", flexDirection: "row", alignItems: "center" }}
      >
        <Box
          mx={1}
          style={{
            display: "inline-block",
            width: "15px",
            height: "15px",
            ...createCheckeredBackground(color),
          }}
        />
        Work time and Entry
        <Box
          mx={1}
          style={{
            display: "inline-block",
            width: "15px",
            height: "15px",
            backgroundColor: color,
          }}
        />
        Entry
        <Box
          mx={1}
          style={{
            display: "inline-block",
            width: "15px",
            height: "15px",
            backgroundColor: "lightgrey",
          }}
        />
        Work time
      </Text>
    </Box>
  );
};

type ConstraintDayProps = {
  day: (typeof DAYS)[number];
  field: "never_work_masks" | "always_work_masks";
  color: string;
  resourceId: string;
  workMask: number;
};

export const ConstraintDay: FC<ConstraintDayProps> = ({
  day,
  field,
  color,
  resourceId,
  workMask,
}) => {
  const theme = useMantineTheme();
  const form = useMasterFormContext();
  const resourceIndex = useSimParamsResourceIndex(resourceId);
  const workTimes = useSimParamsWorkTimes(resourceId, day) ?? [];

  const error = useFormError(
    `constraints.resources.${resourceIndex}.constraints.${field}.${day}`
  );

  const selectedIndexes = bitmaskToSelectionIndexes(workMask ?? 0);
  const style = error ? { borderColor: "red", borderWidth: "1px" } : {};

  return (
    <>
      {HOURS.map((hour, hourIndex) => {
        const hasEvent = selectedIndexes.includes(hourIndex);
        const hasWorkTime = workTimes.some(
          (workTime) =>
            isTimePeriodInDay(workTime, day) &&
            isTimePeriodInHour(workTime, hour)
        );
        const boxStyle =
          hasWorkTime && hasEvent
            ? createCheckeredBackground(color)
            : hasEvent
            ? { backgroundColor: color }
            : hasWorkTime
            ? { backgroundColor: "lightgrey" }
            : {};

        return (
          <Box
            className="element"
            data-index={hourIndex}
            data-day={day}
            key={`event-${day}-${hourIndex}`}
            style={{
              height: 30,
              width: "100%",
              borderColor: theme.colors["gray"][5],
              borderBottomWidth: "1px",
              borderBottomStyle: "solid",
              borderRightWidth: "1px",
              borderRightStyle: "solid",
              ...boxStyle,
            }}
          />
        );
      })}

      {error && (
        <Text ta="center" c="red">
          {error.message}
        </Text>
      )}
    </>
  );
};

const createCheckeredBackground = (
  color: string,
  backgroundColor = "lightgrey"
) => ({
  background: `repeating-linear-gradient(135deg, ${color}, ${color} 5px, ${backgroundColor} 5px, ${backgroundColor} 10px)`,
});
