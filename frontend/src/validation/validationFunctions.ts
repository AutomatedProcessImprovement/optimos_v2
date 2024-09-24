import type { DAYS_UPPERCASE } from "../helpers";
import {
  DAYS,
  bitmaskToSelectionIndexes,
  timePeriodToBinary,
  timePeriodsToBinary,
} from "../helpers";
import type { MasterFormData } from "../hooks/useMasterFormData";
import { TimePeriod } from "../redux/slices/optimosApi";
import {
  getMaxShiftSizeFromBitmask,
  getMaxShiftSizeFromTimePeriods,
  getNumberOfShiftsFromBitmask,
} from "./validationHelper";
import { createFormContext, useForm } from "@mantine/form";

export const getOverlappingHours = (
  day: (typeof DAYS)[number],
  mask: number,
  work_times: TimePeriod[]
) => {
  const workHours = timePeriodsToBinary(work_times, day);

  return bitmaskToSelectionIndexes(mask & workHours);
};

export const createValidateNeverWorkMask =
  (resourceIndex: number, day: (typeof DAYS)[number]) =>
  (mask: number, masterForm: MasterFormData) => {
    const work_times =
      masterForm.simulationParameters!.resource_calendars[resourceIndex]
        .time_periods;

    if (!work_times) return "Resource not found";

    const overlapping_hours = getOverlappingHours(day, mask, work_times);

    if (overlapping_hours.length > 0) {
      return "Resource is working during these hours.";
    }

    return true;
  };

export const createValidateAlwaysWorkMask =
  (resourceIndex: number, day: (typeof DAYS)[number]) =>
  (mask: number, masterForm: MasterFormData) => {
    const never_work_masks =
      masterForm.constraints!.resources[resourceIndex].constraints
        .never_work_masks[day] ?? 0;
    const work_times =
      masterForm.simulationParameters!.resource_calendars[resourceIndex]
        .time_periods;

    if ((mask & never_work_masks) !== 0) {
      return "There is a conflict with the never work hours.";
    }

    const work_mask = timePeriodsToBinary(
      work_times,
      day.toLocaleUpperCase() as (typeof DAYS_UPPERCASE)[number]
    );
    const always_work_outside_timetable = (mask | work_mask) !== work_mask;

    if (always_work_outside_timetable) {
      return "Always work time not in timetable.";
    }

    return true;
  };

type ValidationFnType = Parameters<
  typeof useForm<MasterFormData>
>[0]["validate"];

export const constraintResolver: ValidationFnType = (values) => {
  const constraints = values.constraints;
  const resources = constraints?.resources;
  const resource_calendars = values.simulationParameters?.resource_calendars;

  if (!resources || !resource_calendars) return {};

  const errors: any = {}; // TODO: Improve type

  let overallCapacityTimeTable = 0;
  let overallCapacityAlwaysWork = 0;

  let { max_shift_size, max_shift_blocks } = values.constraints!;

  for (let i = 0; i < resources.length; i++) {
    const resource = resources[i];

    const globalConstraints = resource.constraints.global_constraints;
    let sumOfTimeTableHours = 0;
    let sumOfAlwaysWorkHours = 0;

    const time_periods =
      resource_calendars.find(
        (resource_calendar) => resource_calendar.id === resource.id
      )?.time_periods ?? [];

    // Validate never_work_masks and always_work_masks
    const never_work_masks = resource.constraints.never_work_masks;
    const always_work_masks = resource.constraints.always_work_masks;

    for (const day of DAYS) {
      const never_work_mask = never_work_masks[day];
      const always_work_mask = always_work_masks[day];

      const workTimeMask = timePeriodsToBinary(time_periods, day);

      const sumOfTimeTableHoursDaily =
        workTimeMask.toString(2).split("1").length - 1;
      const sumOfAlwaysWorkHoursDaily =
        always_work_mask.toString(2).split("1").length - 1;

      if (sumOfTimeTableHoursDaily > globalConstraints.max_daily_cap) {
        errors.constraints ??= {};
        errors.constraints.resources ??= [];
        errors.constraints.resources[i] ??= {};
        errors.constraints.resources[i]!.constraints ??= {};
        errors.constraints.resources[i]!.constraints!.global_constraints ??= {};
        errors.constraints.resources[
          i
        ]!.constraints!.global_constraints!.max_daily_cap = {
          type: "validate",
          message: `Daily Capacity exceeded by time table hours ${sumOfTimeTableHoursDaily}h`,
          // @ts-ignore
          fix: sumOfTimeTableHoursDaily,
        };
      }
      if (sumOfAlwaysWorkHoursDaily > globalConstraints.max_daily_cap) {
        errors.constraints ??= {};
        errors.constraints.resources ??= [];
        errors.constraints.resources[i] ??= {};
        errors.constraints.resources[i]!.constraints ??= {};
        errors.constraints.resources[i]!.constraints!.global_constraints ??= {};
        errors.constraints.resources[
          i
        ]!.constraints!.global_constraints!.max_daily_cap = {
          type: "validate",
          message: `Daily Capacity exceeded by always work hours ${sumOfAlwaysWorkHoursDaily}h`,
          // @ts-ignore
          fix: sumOfAlwaysWorkHoursDaily,
        };
      }
      if (sumOfTimeTableHoursDaily > globalConstraints.max_shifts_day) {
        errors.constraints ??= {};
        errors.constraints.resources ??= [];
        errors.constraints.resources[i] ??= {};
        errors.constraints.resources[i]!.constraints ??= {};
        errors.constraints.resources[i]!.constraints!.global_constraints ??= {};
        errors.constraints.resources[
          i
        ]!.constraints!.global_constraints!.max_shifts_day = {
          type: "validate",
          message: `Daily Capacity exceeded by time table hours (${sumOfTimeTableHoursDaily}h)`,
          //@ts-ignore
          fix: sumOfTimeTableHoursDaily,
        };
      }
      if (sumOfAlwaysWorkHoursDaily > globalConstraints.max_shifts_day) {
        errors.constraints ??= {};
        errors.constraints.resources ??= [];
        errors.constraints.resources[i] ??= {};
        errors.constraints.resources[i]!.constraints ??= {};
        errors.constraints.resources[i]!.constraints!.global_constraints ??= {};
        errors.constraints.resources[
          i
        ]!.constraints!.global_constraints!.max_shifts_day = {
          type: "validate",
          message: `Daily Capacity exceeded by always work hours (${sumOfAlwaysWorkHoursDaily}h)`,
          // @ts-ignore
          fix: sumOfAlwaysWorkHoursDaily,
        };
      }

      sumOfTimeTableHours += sumOfTimeTableHoursDaily;
      sumOfAlwaysWorkHours += sumOfAlwaysWorkHoursDaily;

      if (never_work_mask) {
        const validateNeverWorkMask = createValidateNeverWorkMask(i, day);
        const result = validateNeverWorkMask(never_work_mask, values);
        if (result !== true) {
          errors.constraints ??= {};
          errors.constraints.resources ??= [];
          errors.constraints.resources[i] ??= {};
          errors.constraints.resources[i]!.constraints ??= {};
          errors.constraints.resources[i]!.constraints!.never_work_masks ??= {};
          errors.constraints.resources[i]!.constraints!.never_work_masks![day] =
            {
              type: "validate",
              message: result,
            };
        }
      }

      if (always_work_mask) {
        const validateAlwaysWorkMask = createValidateAlwaysWorkMask(i, day);
        const result = validateAlwaysWorkMask(always_work_mask, values);
        if (result !== true) {
          errors.constraints ??= {};
          errors.constraints.resources ??= [];
          errors.constraints.resources[i] ??= {};
          errors.constraints.resources[i]!.constraints ??= {};
          errors.constraints.resources[i]!.constraints!.always_work_masks ??=
            {};
          errors.constraints.resources[i]!.constraints!.always_work_masks![
            day
          ] = {
            type: "validate",
            message: result,
          };
        }
        const maxShiftSize = getMaxShiftSizeFromBitmask(always_work_mask);
        if (maxShiftSize > max_shift_size) {
          errors.constraints ??= {};
          errors.constraints.max_shift_size = {
            type: "validate",
            message: `Shift size exceeded by ${resource.id}'s always work hours (${maxShiftSize})`,
            // @ts-ignore
            fix: maxShiftSize,
          };
        }
        const numberOfShifts = getNumberOfShiftsFromBitmask(always_work_mask);
        if (numberOfShifts > max_shift_blocks) {
          errors.constraints ??= {};
          errors.constraints.max_shift_blocks = {
            type: "validate",
            message: `Shift blocks exceeded by ${resource.id}'s always work hours (${numberOfShifts})`,
            // @ts-ignore
            fix: numberOfShifts,
          };
        }
      }

      const numberOfShifts = getNumberOfShiftsFromBitmask(workTimeMask);
      if (numberOfShifts > max_shift_blocks) {
        errors.constraints ??= {};
        errors.constraints.max_shift_blocks = {
          type: "validate",
          message: `Max Shifts / day exceeded by ${resource.id}'s time table hours (${numberOfShifts})`,
          //@ts-ignore
          fix: numberOfShifts,
        };
      }
      const maxShiftSize = getMaxShiftSizeFromBitmask(workTimeMask);
      if (maxShiftSize > max_shift_size) {
        errors.constraints ??= {};
        errors.constraints.max_shift_size = {
          type: "validate",
          message: `Max Shift Size exceeded by ${resource.id}'s time table hours (${maxShiftSize})`,
          //@ts-ignore
          fix: maxShiftSize,
        };
      }
    }
    if (sumOfTimeTableHours > globalConstraints.max_weekly_cap) {
      errors.constraints ??= {};
      errors.constraints.resources ??= [];
      errors.constraints.resources[i] ??= {};
      errors.constraints.resources[i]!.constraints ??= {};
      errors.constraints.resources[i]!.constraints!.global_constraints ??= {};
      errors.constraints.resources[
        i
      ]!.constraints!.global_constraints!.max_weekly_cap = {
        type: "validate",
        message: `Weekly Capacity exceeded by time table hours (${sumOfTimeTableHours}h)`,
        //@ts-ignore
        fix: sumOfTimeTableHours,
      };
    }

    if (sumOfAlwaysWorkHours > globalConstraints.max_weekly_cap) {
      errors.constraints ??= {};
      errors.constraints.resources ??= [];
      errors.constraints.resources[i] ??= {};
      errors.constraints.resources[i]!.constraints ??= {};
      errors.constraints.resources[i]!.constraints!.global_constraints ??= {};
      errors.constraints.resources[
        i
      ]!.constraints!.global_constraints!.max_weekly_cap = {
        type: "validate",
        message: `Weekly Capacity exceeded by always work hours (${sumOfAlwaysWorkHours}h)`,
        //@ts-ignore
        fix: sumOfAlwaysWorkHours,
      };
    }
    if (sumOfTimeTableHours > globalConstraints.max_shifts_week) {
      errors.constraints ??= {};
      errors.constraints.resources ??= [];
      errors.constraints.resources[i] ??= {};
      errors.constraints.resources[i]!.constraints ??= {};
      errors.constraints.resources[i]!.constraints!.global_constraints ??= {};
      errors.constraints.resources[
        i
      ]!.constraints!.global_constraints!.max_shifts_week = {
        type: "validate",
        message: `Weekly Capacity exceeded by time table (${sumOfTimeTableHours}h)`,
        //@ts-ignore
        fix: sumOfTimeTableHours,
      };
    }

    if (sumOfAlwaysWorkHours > globalConstraints.max_shifts_week) {
      errors.constraints ??= {};
      errors.constraints.resources ??= [];
      errors.constraints.resources[i] ??= {};
      errors.constraints.resources[i]!.constraints ??= {};
      errors.constraints.resources[i]!.constraints!.global_constraints ??= {};
      errors.constraints.resources[
        i
      ]!.constraints!.global_constraints!.max_shifts_week = {
        type: "validate",
        message: `Weekly Capacity exceeded by ${resource.id}'s always work hours (${sumOfAlwaysWorkHours}h)`,
        //@ts-ignore
        fix: sumOfAlwaysWorkHours,
      };
    }
    overallCapacityAlwaysWork += sumOfAlwaysWorkHours;
    overallCapacityTimeTable += sumOfTimeTableHours;
  }

  const maxCapacity = values.constraints?.max_cap ?? 0;

  if (overallCapacityTimeTable > maxCapacity) {
    errors.constraints ??= {};
    errors.constraints.max_cap = {
      type: "validate",
      message: `Weekly Capacity exceeded by time table hours (${overallCapacityTimeTable}h)`,
      //@ts-ignore
      fix: overallCapacityTimeTable,
    };
  }

  if (overallCapacityAlwaysWork > maxCapacity) {
    errors.constraints ??= {};
    errors.constraints.max_cap = {
      type: "validate",
      message: `Weekly Capacity exceeded by always work hours (${overallCapacityAlwaysWork}h)`,
      //@ts-ignore
      fix: overallCapacityAlwaysWork,
    };
  }

  return errors;
};
