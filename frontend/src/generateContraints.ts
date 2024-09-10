import {
  SimParams,
  ConsParams,
  ResourceConstraints,
  GlobalConstraints,
  DailyStartTimes,
  ConstraintWorkMask,
  ResourceCalendar,
} from "./types/optimos_json_type";

const int_week_days = {
  "0": "MONDAY",
  "1": "TUESDAY",
  "2": "WEDNESDAY",
  "3": "THURSDAY",
  "4": "FRIDAY",
  "5": "SATURDAY",
  "6": "SUNDAY",
} as const;
type DayNumber = keyof typeof int_week_days;
const DAY_NUMBERS = Object.keys(int_week_days) as DayNumber[];

interface TimeInterval {
  start: Date;
  end: Date;
  duration: number;
}

interface CalendarInfo {
  work_rest_count: Record<DayNumber, [number, number]>; // [work_count, rest_count]
  work_intervals: Record<DayNumber, TimeInterval[]>;
  total_weekly_work: number; // Assuming total_weekly_work is of seconds
}

export const generateConstraints = (simParams: SimParams): ConsParams => {
  const calendarsMap: Record<string, CalendarInfo> = parseResourceCalendars(
    simParams["resource_calendars"]
  );

  const localConstraints: ResourceConstraints[] = [];

  for (const cId of Object.keys(calendarsMap)) {
    const cInfo = calendarsMap[cId];
    let maxDailyWork = 0;
    let maxConsecutiveCap = 0;
    let minDate: Date | null = null;

    for (const wDay of DAY_NUMBERS) {
      maxDailyWork = Math.max(maxDailyWork, cInfo.work_rest_count[wDay][0]);

      for (const cInterv of cInfo.work_intervals[wDay]) {
        minDate =
          minDate === null
            ? new Date(cInterv.start)
            : new Date(
                Math.min(minDate.getTime(), new Date(cInterv.start).getTime())
              );
        maxConsecutiveCap = Math.max(maxConsecutiveCap, cInterv.duration);
      }
    }

    const globalConstraints: GlobalConstraints = {
      max_weekly_cap: cInfo.total_weekly_work / 3600,
      max_daily_cap: maxDailyWork / 3600,
      max_consecutive_cap: maxConsecutiveCap / 3600,
      max_shifts_day: 24,
      max_shifts_week: cInfo.total_weekly_work / 3600,
      is_human: !cId.toLowerCase().includes("system"),
    };

    const dailyStartTimes: DailyStartTimes = {
      monday: null,
      tuesday: null,
      wednesday: null,
      thursday: null,
      friday: null,
      saturday: null,
      sunday: null,
    };
    const neverWorkMasks: ConstraintWorkMask = {
      monday: 0,
      tuesday: 0,
      wednesday: 0,
      thursday: 0,
      friday: 0,
      saturday: 0,
      sunday: 0,
    };
    const alwaysWorkMasks: ConstraintWorkMask = {
      monday: 0,
      tuesday: 0,
      wednesday: 0,
      thursday: 0,
      friday: 0,
      saturday: 0,
      sunday: 0,
    };

    const minDateStr = minDate
      ? minDate.toTimeString().split(" ")[0]
      : "00:00:00";
    const mask24Hour = 16777215;

    for (const wDay of DAY_NUMBERS) {
      const cDay = int_week_days[
        wDay
      ].toLowerCase() as keyof ConstraintWorkMask;
      dailyStartTimes[cDay] =
        cInfo.work_rest_count[wDay][0] > 0 ? minDateStr : null;
      //neverWorkMasks[cDay] = !dailyStartTimes[cDay] ? mask24Hour : 0;
      alwaysWorkMasks[cDay] = 0; // will keep untouched to always allowing removal
    }

    localConstraints.push({
      id: cId,
      constraints: {
        global_constraints: globalConstraints,
        daily_start_times: dailyStartTimes,
        never_work_masks: neverWorkMasks,
        always_work_masks: alwaysWorkMasks,
      },
    });
  }

  const jsonStruct: ConsParams = {
    time_var: 60,
    max_cap: 9999999999,
    max_shift_size: 24,
    max_shift_blocks: 24,
    hours_in_day: 24,
    resources: localConstraints,
  };

  return jsonStruct;
};

interface TimeInterval {
  start: Date;
  duration: number;
}

interface WorkRestCount {
  [key: number]: [number, number];
}

type WorkIntervals = Record<DayNumber, TimeInterval[]>;

const parseResourceCalendars = (
  resourceCalendars: ResourceCalendar[]
): Record<string, CalendarInfo> => {
  const calendars_info: { [key: string]: any } = {};

  function toSeconds(value: number, unit: string): number {
    switch (unit) {
      default:
      case "SECONDS":
        return value;
      case "MINUTES":
        return value * 60;
      case "HOURS":
        return value * 60 * 60;
      case "DAYS":
        return value * 60 * 60 * 24;
      case "WEEKS":
        return value * 60 * 60 * 24 * 7;
    }
  }

  function computeCumulativeDurations(work_intervals: WorkIntervals): {
    [key: number]: number[];
  } {
    const cumulative_work_durations: { [key: number]: number[] } = {};
    for (const w_day of DAY_NUMBERS) {
      cumulative_work_durations[w_day] = [];
      let cumulative = 0;
      for (const interval of work_intervals[w_day]) {
        cumulative += interval.duration;
        cumulative_work_durations[w_day].push(cumulative);
      }
    }
    return cumulative_work_durations;
  }

  function parseTime(timeStr: string): Date {
    const [hours, minutes, seconds] = timeStr.split(":").map(Number);
    const date = new Date();
    date.setHours(hours, minutes, seconds);
    return date;
  }

  for (const calendars of resourceCalendars) {
    const calendar_id = calendars["id"];
    const default_date = null;
    const new_day = null;
    const work_intervals: WorkIntervals = {
      "0": [],
      "1": [],
      "2": [],
      "3": [],
      "4": [],
      "5": [],
      "6": [],
    };
    const cumulative_work_durations: { [key: number]: number[] } = {};
    const work_rest_count: WorkRestCount = {};
    let total_weekly_work = 0;
    let total_weekly_rest = toSeconds(1, "WEEKS");

    for (const w_day of DAY_NUMBERS) {
      work_intervals[w_day] = [];
      cumulative_work_durations[w_day] = [];
      work_rest_count[w_day] = [0, toSeconds(1, "DAYS")];
    }

    for (const c_item of calendars["time_periods"]) {
      const fromDay = c_item["from"];
      const toDay = c_item["to"];
      const beginTime = parseTime(c_item["beginTime"]);
      const endTime = parseTime(c_item["endTime"]);
      const duration = (endTime.getTime() - beginTime.getTime()) / 1000;
      const w_day = [
        "MONDAY",
        "TUESDAY",
        "WEDNESDAY",
        "THURSDAY",
        "FRIDAY",
        "SATURDAY",
        "SUNDAY",
      ]
        .indexOf(fromDay)
        .toString() as DayNumber;
      const interval: TimeInterval = {
        start: beginTime,
        end: endTime,
        duration: duration,
      };
      work_intervals[w_day].push(interval);
      total_weekly_work += duration;
      total_weekly_rest -= duration;
      work_rest_count[w_day][0] += duration;
      work_rest_count[w_day][1] -= duration;
    }

    const cumulativeDurations = computeCumulativeDurations(work_intervals);

    calendars_info[calendar_id] = {
      calendar_id: calendar_id,
      default_date: default_date,
      new_day: new_day,
      work_intervals: work_intervals,
      cumulative_work_durations: cumulativeDurations,
      work_rest_count: work_rest_count,
      total_weekly_work: total_weekly_work,
      total_weekly_rest: total_weekly_rest,
    };
  }

  return calendars_info;
};
