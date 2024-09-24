import { Table, Text } from "@mantine/core";
import { COLUMN_DEFINITIONS } from "./ResourcesTableColumnDefinitions";

import { FC, memo } from "react";
import React from "react";
import { useInitialResource } from "../../../hooks/useInitialSolution";
import { JsonResourceInfo } from "../../../redux/slices/optimosApi";
import { DiffInfo } from "./DiffInfo";

type ResourcesTableCellProps = {
  column: (typeof COLUMN_DEFINITIONS)[number];
  resource: JsonResourceInfo;
};

export const ResourcesTableCell: FC<ResourcesTableCellProps> = memo(
  ({ column: { id, formatFn, lowerIsBetter }, resource }) => {
    const initial_resource = useInitialResource(resource.id);
    console.log(id, resource, initial_resource);
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
  }
);
