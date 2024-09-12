import { Grid, Box, Text, Divider } from "@mantine/core";
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

  return (
    <Grid className={containerClassName}>
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
        <Grid>
          <Grid.Col span={2} />

          {/* Days headers */}
          {DAYS.map((day, index) => (
            <Grid.Col span={1} key={index}>
              <Text ta="center" fw={500}>
                {day}
              </Text>
            </Grid.Col>
          ))}
        </Grid>
        <Divider />
        <Grid>
          {/* Time column */}
          <Grid.Col span={2}>
            {HOURS.map((hour) => (
              <Grid
                key={`hour-label-${hour}`}
                style={{
                  height: 30,
                  display: "flex",
                  justifyContent: "center",
                  alignItems: "center",
                }}
              >
                <Text size="sm">{`${hour}:00`}</Text>
              </Grid>
            ))}
          </Grid.Col>

          <Grid.Col span={10}>
            <Grid>
              {DAYS.map((day, dayIndex) => (
                <ConstraintDay
                  color={color}
                  key={`constraint-day-${day}`}
                  day={day}
                  field={field}
                  resourceId={resourceId}
                  workMask={workMask[day]}
                />
              ))}
            </Grid>
          </Grid.Col>
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
    </Grid>
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
  const form = useMasterFormContext();
  const resourceIndex = useSimParamsResourceIndex(resourceId);
  const workTimes = useSimParamsWorkTimes(resourceId, day) ?? [];

  const error = form.getInputProps(
    `constraints.resources.${resourceIndex}.constraints.${field}.${day}`
  ).error;

  const selectedIndexes = bitmaskToSelectionIndexes(workMask ?? 0);
  const style = error ? { borderColor: "red", borderWidth: "1px" } : {};

  return (
    <Grid.Col span={1} style={{ borderLeft: "1px solid grey", ...style }}>
      <Grid>
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
              : { borderColor: "grey.300" };

          return (
            <Grid.Col
              className="element"
              data-index={hourIndex}
              data-day={day}
              key={`event-${day}-${hourIndex}`}
              style={{
                height: 30,
                borderBottomWidth: "1px",
                borderBottomStyle: "solid",
                ...boxStyle,
              }}
            />
          );
        })}
      </Grid>
      {error && (
        <Text ta="center" color="red">
          {error.message}
        </Text>
      )}
    </Grid.Col>
  );
};

const createCheckeredBackground = (
  color: string,
  backgroundColor = "lightgrey"
) => ({
  background: `repeating-linear-gradient(135deg, ${color}, ${color} 5px, ${backgroundColor} 5px, ${backgroundColor} 10px)`,
});
