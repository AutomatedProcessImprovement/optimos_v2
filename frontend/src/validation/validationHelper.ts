/* eslint-disable no-fallthrough */
/* eslint-disable no-duplicate-case */
// flat error object

import type { MasterFormData } from "../hooks/useMasterFormData";
import type { DAYS } from "../helpers";
import {
  bitmaskToSelectionIndexes,
  isTimePeriodInDay,
  isTimePeriodInHour,
  selectionIndexesToBitmask,
  timePeriodsToBinary,
} from "../helpers";

import { getOverlappingHours } from "./validationFunctions";

// e.g {a: {b: {c: {message: 'error'}}}} => {'a.b.c': {message: 'error'}}
export const flattenErrors = (errors: FieldErrors<MasterFormData>) => {
  const result: Partial<
    Record<FieldPath<MasterFormData>, GlobalError & { fix?: number }>
  > = {};

  const recurse = (obj: any, path: string) => {
    for (const key in obj) {
      const newPath = path ? `${path}.${key}` : key;
      if (typeof obj[key] === "object" && obj[key]["message"] === undefined) {
        recurse(obj[key], newPath);
      } else {
        result[newPath as FieldPath<MasterFormData>] = obj[key];
      }
    }
  };

  recurse(errors, "");

  return result;
};

export type AutoFix = {
  title: string;
  action: (
    getValues: (_: any) => MasterFormData, // TODO improve type
    setValue: (path: string, value: any) => void
  ) => void;
};

export type ParsedError = {
  humanReadablePath: string;
  message: string;
  path: string;
  link: string;
  humanReadableFieldName: string;
  autoFixes: AutoFix[];
};

export const convertError = (
  error: FieldErrors<MasterFormData>,
  formData: MasterFormData
) => {
  const flattedError = flattenErrors(error);

  return Object.entries(flattedError)
    .map(([path, error]) => {
      const pathArray = path.split(".");
      const prefix = pathArray.slice(0, 2).join(".");

      if (!error) return null;
      switch (prefix) {
        case "constraints.max_cap":
          return {
            humanReadablePath: "Max Capacity",
            message: error.message,
            path,
            link: `?tabIndex=1`,
            humanReadableFieldName: "Max Capacity",
            autoFixes: createScenarioConstraintsQuickFixes(path, error),
          };
        case "constraints.max_shift_size":
          return {
            humanReadablePath: "Max Shift Size",
            message: error.message,
            path,
            link: `?tabIndex=1`,
            humanReadableFieldName: "Max Shift Size",
            autoFixes: createScenarioConstraintsQuickFixes(path, error),
          };
        case "constraints.max_shift_blocks":
          return {
            humanReadablePath: "Max Shift Blocks",
            message: error.message,
            path,
            link: `?tabIndex=1`,
            humanReadableFieldName: "Max Shift Blocks",
            autoFixes: createScenarioConstraintsQuickFixes(path, error),
          };
        case "constraints.resources":
          const resourceIndex = pathArray[2];
          const resource =
            formData.constraints?.resources[parseInt(resourceIndex)].id;

          const field = pathArray.slice(3, 5).join(".");
          console.log("field", field);

          switch (field) {
            case "constraints.never_work_masks":
            case "constraints.always_work_masks":
              const day = pathArray[5];
              const humanReadableFieldName =
                field === "constraints.never_work_masks"
                  ? "Never Work Times"
                  : "Always Work Times";
              return {
                humanReadablePath: `Resource Constraints > ${resource} > ${humanReadableFieldName} > ${day}`,
                message: error.message,
                path,
                link: `?tabIndex=2`,
                humanReadableFieldName,
                autoFixes: createResourceConstraintQuickFixes(
                  path,
                  formData,
                  error
                ),
              };
            case "constraints.global_constraints":
              const globalConstraint = pathArray[5];
              return {
                humanReadablePath: `Resource Constraints > ${resource} > Global Constraints > ${globalConstraint.replaceAll(
                  "_",
                  " "
                )}`,
                message: error.message,
                path,
                link: `?tabIndex=2`,
                humanReadableFieldName: globalConstraint.replace(/_/g, " "),
                autoFixes: createResourceConstraintQuickFixes(
                  path,
                  formData,
                  error
                ),
              };

            default:
              console.log("field", field);
              return null;
          }

        default:
          console.log("prefix", prefix);
          return null;
      }
    })
    .filter((x) => x !== null) as ParsedError[];
};

const createResourceConstraintQuickFixes = (
  path: string,
  formData: MasterFormData,
  error: GlobalError & { fix?: number }
): AutoFix[] => {
  const pathArray = path.split(".");
  const resourceIndex = parseInt(pathArray[2]);
  const resourceId = formData.constraints?.resources[resourceIndex].id;

  const field = pathArray.slice(3, 5).join(".");

  switch (field) {
    case "constraints.never_work_masks":
      return [
        {
          title: "Remove from Timetable",
          action: (get, set) => {
            const day = pathArray[5] as (typeof DAYS)[number];
            const calendars = get("simulationParameters.resource_calendars");
            const simParamsCalendarIndex = calendars.findIndex(
              (calendar) => calendar.id === resourceId
            );
            const timePeriods =
              calendars[simParamsCalendarIndex]?.time_periods ?? [];
            const neverWorkMasks = get(path as any);
            const overlappingHours = getOverlappingHours(
              day,
              neverWorkMasks,
              timePeriods
            );
            const newTimePeriods = removeManyFromTimetable(
              day,
              overlappingHours,
              timePeriods
            );
            set(
              `simulationParameters.resource_calendars.${simParamsCalendarIndex}.time_periods`,
              newTimePeriods
            );
          },
        },
        {
          title: "Remove from Never-Work",
          action: (get, set) => {
            const day = pathArray[5] as (typeof DAYS)[number];
            const calendars = get("simulationParameters.resource_calendars");
            const simParamsCalendarIndex = calendars.findIndex(
              (calendar) => calendar.id === resourceId
            );
            const timePeriods =
              calendars[simParamsCalendarIndex]?.time_periods ?? [];
            const neverWorkMasks = get(path as any);
            const overlappingHours = getOverlappingHours(
              day,
              neverWorkMasks,
              timePeriods
            );
            const overlappingHoursMask =
              selectionIndexesToBitmask(overlappingHours);
            const newNeverWorkMasks = neverWorkMasks & ~overlappingHoursMask;

            set(path as any, newNeverWorkMasks);
          },
        },
      ];
    case "constraints.always_work_masks":
      if (error.message === "Always work time not in timetable.") {
        return [
          {
            title: "Add to Timetable",
            action: (get, set) => {
              const day = pathArray[5] as (typeof DAYS)[number];
              const calendars = get("simulationParameters.resource_calendars");
              const simParamsCalendarIndex = calendars.findIndex(
                (calendar) => calendar.id === resourceId
              );
              const timePeriods =
                calendars[simParamsCalendarIndex]?.time_periods ?? [];
              const alwaysWorkMasks = get(path as any) as number;

              const newTimePeriods = addManyToTimeTable(
                day,
                alwaysWorkMasks,
                timePeriods
              );
              set(
                `simulationParameters.resource_calendars.${simParamsCalendarIndex}.time_periods`,
                newTimePeriods
              );
            },
          },
          {
            title: "Remove from Always-Work",
            action: (get, set) => {
              const day = pathArray[5] as (typeof DAYS)[number];
              const alwaysWorkMasks = get(path as any);
              const calendars = get("simulationParameters.resource_calendars");
              const simParamsCalendarIndex = calendars.findIndex(
                (calendar) => calendar.id === resourceId
              );
              const timePeriods =
                calendars[simParamsCalendarIndex]?.time_periods ?? [];
              const overlappingHours = getOverlappingHours(
                day,
                alwaysWorkMasks,
                timePeriods
              );
              const overlappingHoursMask =
                selectionIndexesToBitmask(overlappingHours);
              const newAlwaysWorkMasks =
                alwaysWorkMasks & ~overlappingHoursMask;

              set(path as any, newAlwaysWorkMasks);
            },
          },
        ];
      }
      return [
        {
          title: "Remove from Never-Work",
          action: (get, set) => {
            const day = pathArray[5] as (typeof DAYS)[number];
            const neverWorkMasks = get(
              `constraints.resources.${resourceIndex}.constraints.never_work_masks.${day}`
            );
            const alwaysWorkMasks = get(path as any);
            const newNeverWorkMask = neverWorkMasks & ~alwaysWorkMasks;

            set(
              `constraints.resources.${resourceIndex}.constraints.never_work_masks.${day}`,
              newNeverWorkMask
            );
          },
        },
        {
          title: "Remove from Always-Work",
          action: (get, set) => {
            const day = pathArray[5] as (typeof DAYS)[number];
            const alwaysWorkMasks = get(path as any);
            const neverWorkMasks = get(
              `constraints.resources.${resourceIndex}.constraints.never_work_masks.${day}`
            );
            const newAlwaysWorkMasks = alwaysWorkMasks & ~neverWorkMasks;

            set(path as any, newAlwaysWorkMasks);
          },
        },
      ];
    case "constraints.global_constraints":
      const subField = pathArray[5];
      if (!error.fix) return [];
      return [
        {
          title: `Set ${subField.replaceAll("_", " ")} max to ${error.fix}`,
          action: (get, set) => {
            set(path as any, error.fix);
          },
        },
      ];
    default:
      return [];
  }
};

export const createScenarioConstraintsQuickFixes = (
  path: string,
  error: GlobalError & { fix?: number }
): AutoFix[] => {
  const fix = error.fix;
  if (!fix) return [];

  switch (path) {
    case "constraints.max_cap":
      return [
        {
          title: `Set Max Capacity to ${fix}`,
          action: (get, set) => {
            set("constraints.max_cap", fix);
          },
        },
      ];
    case "constraints.max_shift_size":
      return [
        {
          title: `Set Max Shift Size to ${fix}`,
          action: (get, set) => {
            set("constraints.max_shift_size", fix);
          },
        },
      ];
    case "constraints.max_shift_blocks":
      return [
        {
          title: `Set Max Shift Blocks to ${fix}`,
          action: (get, set) => {
            set("constraints.max_shift_blocks", fix);
          },
        },
      ];
    default:
      return [];
  }
};

export const addManyToTimeTable = (
  day: (typeof DAYS)[number],
  always_work_mask: number,
  timePeriods: TimePeriod[]
) => {
  const bitmask = timePeriodsToBinary(timePeriods, day);
  const new_time_period_bitmask = always_work_mask | bitmask;

  const indices = bitmaskToSelectionIndexes(new_time_period_bitmask);
  if (indices.length === 0) {
    return timePeriods;
  }

  const new_time_periods = timePeriods.filter(
    (timePeriod) => !isTimePeriodInDay(timePeriod, day)
  );
  // Go through the indices, and add the time periods to the timetable.
  // We are smart about it, e.g. grouping continuous hours together in one time period
  let beginTime: number | null = null;
  let lastHour: number | null = null;
  for (const index of indices) {
    if (lastHour === null) {
      beginTime = index;
      lastHour = index;
    } else if (index === lastHour + 1) {
      // We are still in the same time period
      lastHour = index;
    } else {
      // We are in a new time period
      new_time_periods.push({
        beginTime: `${beginTime!.toString().padStart(2, "0")}:00:00`,
        endTime: `${(lastHour + 1).toString().padStart(2, "0")}:00:00`,
        from: day.toLocaleUpperCase(),
        to: day.toLocaleUpperCase(),
      });
      beginTime = index;
      lastHour = index;
    }
  }
  if (lastHour !== null && beginTime !== null) {
    // Add the last time period
    new_time_periods.push({
      beginTime: `${beginTime.toString().padStart(2, "0")}:00:00`,
      endTime: `${(lastHour! + 1).toString().padStart(2, "0")}:00:00`,
      from: day.toLocaleUpperCase(),
      to: day.toLocaleUpperCase(),
    });
  }
  return new_time_periods;
};

export const removeManyFromTimetable = (
  day: string,
  hours: number[],
  timePeriods: TimePeriod[]
) => {
  let updatedTimePeriods = timePeriods;

  for (const hour of hours) {
    updatedTimePeriods = removeTimeFromTimetable(day, hour, updatedTimePeriods);
  }
  return updatedTimePeriods;
};

// Removes a time from the timetable of a resource
// This means, that we need to split/shorten the time periods that are containg the hour
// (e.g. if we remove 10:00 from 9:00-12:00, we need to split it into 9:00-10:00 and 11:00-12:00,
// if we remove 10:00 from 10:00-11:00, we need to remove the whole time period
// if we remove 10:00 from 08:00-10:00;10:00-12:00, we need to shorten the first to 08:00-09:00,
// and the second to 11:00-12:00)
export const removeTimeFromTimetable = (
  day: string,
  hour: number,
  timePeriods: TimePeriod[]
) => {
  const updatedTimePeriods: TimePeriod[] = [];

  for (const period of timePeriods) {
    if (!isTimePeriodInDay(period, day)) {
      updatedTimePeriods.push(period);
      continue;
    }

    const c = (beginTime: string, endTime: string) => ({
      ...period,
      beginTime,
      endTime,
    });
    let { beginTime, endTime } = period;
    const [startHour, endHour] = [beginTime, endTime].map((time) =>
      parseInt(time.split(":")[0])
    );
    const nextHour = hour + 1;
    const p = (t: number) => t.toString().padStart(2, "0");

    if (startHour === hour && endHour === nextHour) {
      continue;
    } else if (startHour < hour && endHour > nextHour) {
      updatedTimePeriods.push(c(beginTime, `${p(hour)}:00`));
      updatedTimePeriods.push(c(`${p(nextHour)}:00`, endTime));
    } else if (startHour === hour) {
      updatedTimePeriods.push(c(`${p(nextHour)}:00`, endTime));
    } else if (endHour === nextHour) {
      updatedTimePeriods.push(c(beginTime, `${p(hour)}:00`));
    } else {
      updatedTimePeriods.push(period);
    }
  }

  return updatedTimePeriods;
};

export const getMaxShiftSizeFromTimePeriods = (timePeriods: TimePeriod[]) => {
  return timePeriods.reduce((max, { beginTime, endTime }) => {
    const shiftSize =
      parseInt(endTime.split(":")[0]) - parseInt(beginTime.split(":")[0]);
    return shiftSize > max ? shiftSize : max;
  }, 0);
};

export const getMaxShiftSizeFromBitmask = (bitmask: number) => {
  return bitmask
    .toString(2)
    .split("1")
    .reduce((max, block) => {
      const shiftSize = block.length;
      return shiftSize > max ? shiftSize : max;
    }, 0);
};

export const getNumberOfShiftsFromBitmask = (bitmask: number) => {
  return bitmask.toString(2).split("1").length - 1;
};

export const getNumberOfShiftsFromTimePeriods = (timePeriods: TimePeriod[]) => {
  return timePeriods.length;
};
