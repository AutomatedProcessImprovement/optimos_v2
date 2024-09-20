import { Table, Text } from "@mantine/core";
import { COLUMN_DEFINITIONS } from "./ResourcesTableColumnDefinitions";

import { FC } from "react";
import React from "react";
import { JSONResourceInfo } from "../../../types/optimos_json_type";
import { useInitialResource } from "../../../hooks/useInitialSolution";

type ResourcesTableCellProps = {
  column: (typeof COLUMN_DEFINITIONS)[number];
  resource: JSONResourceInfo;
};

// Did the value change more than 5%?
const changeIsSignificant = (a: any, b: any, margin = 0.05) => {
  if (typeof a !== "number" || typeof b !== "number") return false;
  if (a === b) return false;
  const change = Math.abs(a - b);
  return change / Math.max(a, b) > margin;
};

export const ResourcesTableCell: FC<ResourcesTableCellProps> = ({
  column: { id, formatFn, lowerIsBetter },
  resource,
}) => {
  const initial_resource = useInitialResource(id);
  return (
    <Table.Td key={id} align="left">
      {formatFn(resource[id])}
      <br />
      {lowerIsBetter !== undefined &&
        !resource.modifiers.deleted &&
        !resource.modifiers.added &&
        !!initial_resource?.[id] && (
          <DiffInfo
            a={initial_resource[id]}
            b={resource[id]}
            formatFn={formatFn}
            lowerIsBetter={lowerIsBetter}
          />
        )}
    </Table.Td>
  );
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
    <Text size="xs" color={lowerIsBetter ? "red" : "green"}>
      (↑) {formatFn(onlyShowDiff ? b - a : a)}{" "}
      {onlyShowDiff ? `more than ${suffix}` : suffix}
    </Text>
  ) : (
    <Text size="xs" color={lowerIsBetter ? "green" : "red"}>
      (↓) {formatFn(onlyShowDiff ? a - b : a)}{" "}
      {onlyShowDiff ? `less than ${suffix}` : suffix}
    </Text>
  );
