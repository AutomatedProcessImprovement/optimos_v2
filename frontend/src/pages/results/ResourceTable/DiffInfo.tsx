import { Text } from "@mantine/core";
import React, { FC } from "react";
import { COLUMN_DEFINITIONS } from "./ResourcesTableColumnDefinitions";
// Did the value change more than 5%?
const changeIsSignificant = (a: any, b: any, margin = 0.05) => {
  if (typeof a !== "number" || typeof b !== "number") return false;
  if (a === b) return false;
  const change = Math.abs(a - b);
  return change / Math.max(a, b) > margin;
};

export const DiffInfo: FC<{
  a: any;
  b: any;
  formatFn: (typeof COLUMN_DEFINITIONS)[number]["formatFn"];
  lowerIsBetter: boolean;
  suffix?: string;
  margin?: number;
  onlyShowDiff?: boolean;
}> = ({
  a,
  b,
  formatFn,
  lowerIsBetter,
  suffix,
  margin,
  onlyShowDiff = false,
}) =>
  !changeIsSignificant(a, b, margin) ? null : a < b ? (
    <Text size="xs" color={lowerIsBetter ? "red" : "green"} component="span">
      (↑) {formatFn(onlyShowDiff ? b - a : a)}{" "}
      {onlyShowDiff ? `more than ${suffix}` : suffix}
    </Text>
  ) : (
    <Text size="xs" color={lowerIsBetter ? "green" : "red"} component="span">
      (↓) {formatFn(onlyShowDiff ? a - b : a)}{" "}
      {onlyShowDiff ? `less than ${suffix}` : suffix}
    </Text>
  );
