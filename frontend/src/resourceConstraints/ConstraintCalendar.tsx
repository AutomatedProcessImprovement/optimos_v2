import { Grid, Box, Typography, Divider } from "@mui/material";
import type { FC } from "react";
import { useRef, useEffect, useMemo } from "react";
import Selecto from "react-selecto";
import type { ConstraintWorkMask, TimePeriod } from "~/shared/optimos_json_type";
import { DAYS, HOURS, bitmaskToSelectionIndexes, isTimePeriodInDay, isTimePeriodInHour } from "../helpers";
import { useController, useFormContext, useWatch } from "react-hook-form";
import { MasterFormData } from "../hooks/useMasterFormData";
import { useSimParamsResourceIndex, useSimParamsWorkTimes } from "../hooks/useSimParamsWorkTimes";

type ConstraintCalendarProps = {
  field: "never_work_masks" | "always_work_masks";
  color: string;
  resourceId: string;
  onSelectChange: (selection: Array<HTMLElement | SVGElement>) => void;
};

export const ConstraintCalendar: FC<ConstraintCalendarProps> = ({ field, onSelectChange, color, resourceId }) => {
  const selectoRef = useRef<Selecto | null>(null);
  const { control } = useFormContext<MasterFormData>();

  const containerClassName = `${field}-container`;

  const resources = useWatch({ control: control, name: `constraints.resources` });
  const workMask = resources.find((resource) => resource.id === resourceId)?.constraints[field] as ConstraintWorkMask;

  useEffect(() => {
    // Finds the selected element by data-column, data-day and data-index
    const targets = document.querySelectorAll<HTMLElement>(`.${containerClassName} .element`);
    const selectedTargets = Array.from(targets.values()).filter((element) => {
      const index = parseInt(element.dataset.index!);

      const day = element.dataset.day as (typeof DAYS)[number];
      return (workMask?.[day] ?? 0) & (1 << (23 - index));
    });
    selectoRef.current?.setSelectedTargets(selectedTargets);
  }, [containerClassName, workMask]);
  return (
    <Grid item xs={12} className={containerClassName}>
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
        <Grid container spacing={1}>
          <Grid item xs={2} />

          {/* Days headers */}
          {DAYS.map((day, index) => (
            <Grid item xs key={index}>
              <Typography align="center" variant="h6">
                {day}
              </Typography>
            </Grid>
          ))}
        </Grid>
        <Divider />
        <Grid container>
          {/* Time column */}
          <Grid item xs={2}>
            {HOURS.map((hour) => (
              <Grid
                height={30}
                key={`hour-label-${hour}`}
                container
                direction={"row"}
                alignItems={"center"}
                justifyContent={"center"}
              >
                <Box key={hour} textAlign="center">
                  <Typography variant="body2">{`${hour}:00`}</Typography>
                </Box>
              </Grid>
            ))}
          </Grid>

          <Grid container item direction={"row"} xs>
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
        </Grid>
      </Box>
      <Typography variant="caption" color="textSecondary" flexDirection={"row"}>
        <Box
          mx={1}
          display={"inline-block"}
          width={"15px"}
          height={"15px"}
          style={createCheckeredBackground(color)}
        ></Box>
        Work time and Entry
        <Box mx={1} display={"inline-block"} width={"15px"} height={"15px"} style={{ backgroundColor: color }}></Box>
        Entry
        <Box
          mx={1}
          display={"inline-block"}
          width={"15px"}
          height={"15px"}
          style={{ backgroundColor: "lightgrey" }}
        ></Box>
        Work time
      </Typography>
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
export const ConstraintDay: FC<ConstraintDayProps> = ({ day, field, color, resourceId, workMask }) => {
  const { control } = useFormContext<MasterFormData>();
  const resourceIndex = useSimParamsResourceIndex(resourceId);
  const workTimes = useSimParamsWorkTimes(resourceId, day) ?? [];

  const {
    fieldState: { error },
  } = useController({
    control,
    name: `constraints.resources.${resourceIndex}.constraints.${field}.${day}`,
  });

  const selectedIndexes = bitmaskToSelectionIndexes(workMask ?? 0);
  const style = error ? { borderColor: "red", borderWidth: "1px" } : {};

  return (
    <Grid item xs borderLeft={1} borderColor={"grey"} style={style}>
      <Grid container direction={"column"}>
        {HOURS.map((hour, hourIndex) => {
          const hasEvent = selectedIndexes.includes(hourIndex);
          const hasWorkTime = workTimes.some(
            (workTime) => isTimePeriodInDay(workTime, day) && isTimePeriodInHour(workTime, hour)
          );
          const style =
            hasWorkTime && hasEvent
              ? createCheckeredBackground(color)
              : hasEvent
              ? { backgroundColor: color }
              : hasWorkTime
              ? { backgroundColor: "lightgrey" }
              : { borderColor: "grey.300" };
          return (
            <Grid className="element" data-index={hourIndex} data-day={day} item key={`event-${day}-${hourIndex}`}>
              <Box style={style} borderBottom={1} borderColor="grey.300" width={"100%"} height={30}></Box>
            </Grid>
          );
        })}
      </Grid>
      {error && (
        <Typography textAlign={"center"} color="error">
          {error.message}
        </Typography>
      )}
    </Grid>
  );
};

const createCheckeredBackground = (color: string, backgroundColor = "lightgrey") => ({
  background: `repeating-linear-gradient(135deg, ${color}, ${color} 5px, ${backgroundColor} 5px, ${backgroundColor} 10px)`,
});
