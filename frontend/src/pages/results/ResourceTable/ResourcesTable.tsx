import { Table, Paper, Text, Box, UnstyledButton } from "@mantine/core";
import { IconChevronUp, IconChevronDown } from "@tabler/icons-react";
import type { FC } from "react";
import React, { useCallback, useEffect, useState } from "react";

import { COLUMN_DEFINITIONS } from "./ResourcesTableColumnDefinitions";
import { ResourceTableRow } from "./ResourcesTableRow";
import {
  JsonResourceInfo,
  JsonSolution,
} from "../../../redux/slices/optimosApi";

type OrderByField =
  | keyof Omit<JsonResourceInfo, "initial_resource">
  | "has_changes";
type Order = "asc" | "desc";

type ResourcesTableProps = {
  solution: JsonSolution;
};

const orderByHelper = (a: any, b: any, order: Order) => {
  if (a < b) {
    return order === "desc" ? -1 : 1;
  }
  if (a > b) {
    return order === "desc" ? 1 : -1;
  }
  return 0;
};

const getOrderByHasChangesValue = (resource: JsonResourceInfo) => {
  if (resource.modifiers.deleted) return "1";
  if (resource.modifiers.added) return "2";
  if (resource.modifiers.tasks_modified) return "3";
  if (resource.modifiers.shiftsModified) return "4";
  return "5";
};

export const ResourcesTable: FC<ResourcesTableProps> = React.memo(
  ({ solution }) => {
    const resourceInfo = Object.values(solution.resourceInfo);
    const deletedResourcesInfo = Object.values(solution.deletedResourcesInfo);

    const [orderBy, setOrderBy] = useState<OrderByField>("has_changes");
    const [order, setOrder] = useState<Order>("desc");

    const [sortedResources, setSortedResources] = useState<JSONResourceInfo[]>([
      ...resourceInfo,
      ...deletedResourcesInfo,
    ]);

    useEffect(() => {
      setSortedResources(
        [...sortedResources].sort((a, b) => {
          if (orderBy === "has_changes") {
            return orderByHelper(
              getOrderByHasChangesValue(a),
              getOrderByHasChangesValue(b),
              order
            );
          }
          return orderByHelper(a[orderBy], b[orderBy], order);
        })
      );
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [order, orderBy]);

    const onSortingClick = useCallback(
      (columnId: OrderByField) => {
        if (orderBy !== columnId) {
          setOrder("desc");
          setOrderBy(columnId);
        } else {
          setOrder(order === "asc" ? "desc" : "asc");
        }
      },
      [orderBy, order]
    );

    return (
      <Paper>
        <Table>
          <thead>
            <tr>
              <th />
              <th>
                <UnstyledButton onClick={() => onSortingClick("has_changes")}>
                  <Text>Status</Text>
                  {orderBy === "has_changes" ? (
                    <Box component="span">
                      {order === "desc" ? (
                        <IconChevronDown size={16} />
                      ) : (
                        <IconChevronUp size={16} />
                      )}
                    </Box>
                  ) : null}
                </UnstyledButton>
              </th>
              {COLUMN_DEFINITIONS.map((column) => (
                <th key={column.id} style={{ minWidth: column.minWidth }}>
                  <UnstyledButton onClick={() => onSortingClick(column.id)}>
                    <Text>{column.label}</Text>
                    {orderBy === column.id ? (
                      <Box component="span">
                        {order === "desc" ? (
                          <IconChevronDown size={16} />
                        ) : (
                          <IconChevronUp size={16} />
                        )}
                      </Box>
                    ) : null}
                  </UnstyledButton>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {sortedResources.map((resource) => (
              <ResourceTableRow key={resource.id} resource={resource} />
            ))}
          </tbody>
        </Table>
      </Paper>
    );
  }
);
