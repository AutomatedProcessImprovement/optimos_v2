import type { ReactNode } from "react";

import {
  formatSeconds,
  formatPercentage,
  formatHourlyRate,
  formatCurrency,
  formatHours,
} from "../../../util/num_helper";
import { JsonResourceInfo } from "../../../redux/slices/optimosApi";

export const COLUMN_DEFINITIONS: {
  id: keyof JsonResourceInfo;
  label: string;
  formatFn: (x: any) => ReactNode;
  lowerIsBetter?: boolean;
  minWidth?: string | number;
}[] = [
  { id: "name", label: "Name", formatFn: (x) => x, minWidth: "10em" },
  {
    id: "worked_time",
    label: "Worktime (Calendar)",
    formatFn: formatSeconds,
    lowerIsBetter: true,
    minWidth: "10em",
  },
  {
    id: "available_time",
    label: "Worktime (Actual)",
    formatFn: formatSeconds,
    lowerIsBetter: false,
  },
  {
    id: "utilization",
    label: "Utilization",
    formatFn: formatPercentage,
    lowerIsBetter: false,
  },
  {
    id: "hourly_rate",
    label: "Hourly Rate",
    formatFn: formatHourlyRate,
    lowerIsBetter: true,
  },
  {
    id: "total_batching_waiting_time",
    label: "Batching Waiting Time",
    formatFn: formatSeconds,
    lowerIsBetter: true,
  },
  { id: "is_human", label: "Type", formatFn: (x) => (x ? "Human" : "Machine") },
  {
    id: "cost_per_week",
    label: "Cost/week",
    formatFn: formatCurrency,
    lowerIsBetter: true,
  },
  {
    id: "max_weekly_capacity",
    label: "Max h/week",
    formatFn: formatHours,
    lowerIsBetter: false,
  },
  {
    id: "max_daily_capacity",
    label: "Max h/day",
    formatFn: formatHours,
    lowerIsBetter: false,
  },
  {
    id: "max_consecutive_capacity",
    label: "Max Hours consecutively",
    formatFn: formatHours,
    lowerIsBetter: false,
  },
];
