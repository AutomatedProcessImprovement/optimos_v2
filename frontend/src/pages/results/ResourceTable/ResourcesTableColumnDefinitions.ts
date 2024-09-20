import type { ReactNode } from "react";

import { JSONResourceInfo } from "../../../types/optimos_json_type";
import {
  formatSeconds,
  formatPercentage,
  formatHourlyRate,
  formatCurrency,
  formatHours,
} from "../../../util/num_helper";

export const COLUMN_DEFINITIONS: {
  id: keyof JSONResourceInfo;
  label: string;
  formatFn: (x: any) => ReactNode;
  lowerIsBetter?: boolean;
  minWidth?: string | number;
}[] = [
  { id: "name", label: "Name", formatFn: (x) => x, minWidth: "10em" },
  {
    id: "workedTime",
    label: "Worktime (Calendar)",
    formatFn: formatSeconds,
    lowerIsBetter: false,
    minWidth: "10em",
  },
  {
    id: "availableTime",
    label: "Worktime (Actual)",
    formatFn: formatSeconds,
    lowerIsBetter: true,
  },
  {
    id: "utilization",
    label: "Utilization",
    formatFn: formatPercentage,
    lowerIsBetter: false,
  },
  {
    id: "hourlyRate",
    label: "Hourly Rate",
    formatFn: formatHourlyRate,
    lowerIsBetter: true,
  },
  {
    id: "totalBatchingWaitingTime",
    label: "Batching Waiting Time",
    formatFn: formatSeconds,
    lowerIsBetter: true,
  },
  { id: "isHuman", label: "Type", formatFn: (x) => (x ? "Human" : "Machine") },
  {
    id: "costPerWeek",
    label: "Cost/week",
    formatFn: formatCurrency,
    lowerIsBetter: true,
  },
  {
    id: "maxWeeklyCapacity",
    label: "Max h/week",
    formatFn: formatHours,
    lowerIsBetter: false,
  },
  {
    id: "maxDailyCapacity",
    label: "Max h/day",
    formatFn: formatHours,
    lowerIsBetter: false,
  },
  {
    id: "maxConsecutiveCapacity",
    label: "Max Hours consecutively",
    formatFn: formatHours,
    lowerIsBetter: false,
  },
];
