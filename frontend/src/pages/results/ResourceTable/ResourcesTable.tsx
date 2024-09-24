import { Table, Paper, Text, Box, Button } from "@mantine/core";
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
  if (resource.modifiers.shifts_modified) return "4";
  return "5";
};

export const ResourcesTable: FC<ResourcesTableProps> = React.memo(
  ({ solution }) => {
    const resourceInfo = Object.values(solution.resource_info);
    const deletedResourcesInfo = Object.values(solution.deleted_resources_info);

    const [orderBy, setOrderBy] = useState<OrderByField>("has_changes");
    const [order, setOrder] = useState<Order>("desc");

    const [sortedResources, setSortedResources] = useState<JsonResourceInfo[]>([
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
        <Table.ScrollContainer minWidth={1300}>
          <Table>
            <Table.Thead>
              <Table.Tr>
                <Table.Th />
                <Table.Th>
                  <Button
                    variant="white"
                    color="black"
                    size="compact-sm"
                    onClick={() => onSortingClick("has_changes")}
                    leftSection={
                      orderBy === "has_changes" ? (
                        <>
                          {order === "desc" ? (
                            <IconChevronDown size={16} />
                          ) : (
                            <IconChevronUp size={16} />
                          )}
                        </>
                      ) : null
                    }
                  >
                    Status
                  </Button>
                </Table.Th>
                {COLUMN_DEFINITIONS.map((column) => (
                  <Table.Th
                    key={column.id}
                    style={{ minWidth: column.minWidth }}
                  >
                    <Button
                      size="compact-sm"
                      variant="white"
                      color="black"
                      onClick={() => onSortingClick(column.id)}
                      leftSection={
                        orderBy === column.id ? (
                          <>
                            {order === "desc" ? (
                              <IconChevronDown size={16} />
                            ) : (
                              <IconChevronUp size={16} />
                            )}
                          </>
                        ) : null
                      }
                    >
                      {column.label}
                    </Button>
                  </Table.Th>
                ))}
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {sortedResources.map((resource) => (
                <ResourceTableRow key={resource.id} resource={resource} />
              ))}
            </Table.Tbody>
          </Table>
        </Table.ScrollContainer>
      </Paper>
    );
  }
);
