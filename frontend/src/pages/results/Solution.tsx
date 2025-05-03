import {
  Accordion,
  Button,
  Group,
  Grid,
  Paper,
  Text,
  Box,
} from "@mantine/core";
import {
  IconDownload,
  IconChevronDown,
  IconChevronUp,
} from "@tabler/icons-react";
import React, { FC } from "react";
import { useEffect, useRef, useState, memo, useContext } from "react";
import {
  formatCurrency,
  formatSeconds,
  formatPercentage,
} from "../../util/num_helper";
import { ResourcesTable } from "./ResourceTable/ResourcesTable";
import { ConstraintsType, JsonSolution } from "../../redux/slices/optimosApi";
import { useInitialSolution } from "../../hooks/useInitialSolution";
import { BatchingOverview } from "./BatchingOverview";
import { ModificationOverview } from "./ModificationOverview";
import { DiffInfo } from "./ResourceTable/DiffInfo";

interface OptimosSolutionProps {
  solution: JsonSolution;
  finalMetrics?: any;
  constraints: ConstraintsType;
}

export const OptimosSolution: FC<OptimosSolutionProps> = memo(
  ({ finalMetrics, solution, constraints }) => {
    const initialSolution = useInitialSolution();

    const [expanded, setExpanded] = useState<string | null>(null);

    const link2DownloadRef = useRef<HTMLAnchorElement>(null);
    const link3DownloadRef = useRef<HTMLAnchorElement>(null);

    const [fileDownloadSimParams, setFileDownloadSimParams] = useState("");
    const [fileDownloadConsParams, setFileDownloadConsParams] = useState("");

    const onDownloadEntrySimParams = (entry: any) => {
      const blob = new Blob([JSON.stringify(entry)], {
        type: "application/json",
      });
      const entry_parameters_file = new File([blob], "name", {
        type: "application/json",
      });
      const fileDownloadUrl = URL.createObjectURL(entry_parameters_file);
      setFileDownloadSimParams(fileDownloadUrl);
    };

    const onDownloadEntryConsParams = (entry: any) => {
      const blob = new Blob([JSON.stringify(entry)], {
        type: "application/json",
      });
      const entry_parameters_file = new File([blob], "name", {
        type: "application/json",
      });
      const fileDownloadUrl = URL.createObjectURL(entry_parameters_file);
      setFileDownloadConsParams(fileDownloadUrl);
    };

    useEffect(() => {
      if (fileDownloadSimParams) {
        link2DownloadRef.current?.click();
        URL.revokeObjectURL(fileDownloadSimParams);
      }
    }, [fileDownloadSimParams]);

    useEffect(() => {
      if (fileDownloadConsParams) {
        link3DownloadRef.current?.click();
        URL.revokeObjectURL(fileDownloadConsParams);
      }
    }, [fileDownloadConsParams]);

    const handleChange =
      (panel: string) => (event: React.SyntheticEvent, isExpanded: boolean) => {
        setExpanded(isExpanded ? panel : false);
      };

    return (
      <Paper shadow="sm" p="md" mt="md" ta="left">
        <Grid justify="space-between" align="stretch" style={{ height: "4em" }}>
          <Grid.Col span={7}>
            <Text size="lg" fw={500} tt="capitalize" ta="left">
              {solution.is_base_solution
                ? "Initial Solution"
                : `Solution #${solution.solution_no}`}
            </Text>
          </Grid.Col>
          <Grid.Col span={5}>
            <a
              style={{ display: "none" }}
              download="constraints.json"
              href={fileDownloadConsParams}
              ref={link3DownloadRef}
            >
              Download json
            </a>
            <a
              style={{ display: "none" }}
              download="simparams.json"
              href={fileDownloadSimParams}
              ref={link2DownloadRef}
            >
              Download json
            </a>
            <Button.Group>
              <Button
                fullWidth
                variant="outline"
                size="xs"
                onClick={() => onDownloadEntrySimParams(solution.timetable)}
                leftSection={<IconDownload />}
              >
                Parameters
              </Button>
              <Button
                fullWidth
                variant="outline"
                size="xs"
                onClick={() => onDownloadEntryConsParams(constraints)}
                leftSection={<IconDownload />}
              >
                Constraints
              </Button>
            </Button.Group>
          </Grid.Col>
        </Grid>

        <Accordion
          defaultValue="details"
          value={expanded}
          onChange={setExpanded}
        >
          <Accordion.Item value="details">
            <Accordion.Control>Details</Accordion.Control>
            <Accordion.Panel>
              {expanded == "details" && (
                <Grid justify="flex-start" ta="left">
                  <Grid.Col span={5}>
                    <Text size="sm" fw="bold">
                      Mean cost (work time only - per case)
                    </Text>
                    <Text size="sm" fw="bold">
                      Total cost (available time - all cases)
                    </Text>
                    <Text size="sm" fw="bold">
                      Mean time (per case)
                    </Text>
                    <Text size="sm" fw="bold">
                      Total time (all cases)
                    </Text>
                    <Text size="sm" fw="bold">
                      Mean waiting time (per case)
                    </Text>
                    <Text size="sm" fw="bold">
                      Mean resource utilization
                    </Text>
                  </Grid.Col>
                  <Grid.Col span={7}>
                    <Text size="sm">
                      {formatCurrency(solution.global_info.average_cost)}{" "}
                      <DiffInfo
                        a={initialSolution?.global_info.average_cost}
                        b={solution.global_info.average_cost}
                        formatFn={formatCurrency}
                        lowerIsBetter
                        suffix="initial solution"
                        onlyShowDiff
                      />
                    </Text>
                    <Text size="sm">
                      {formatCurrency(solution.global_info.total_cost)}{" "}
                      <DiffInfo
                        a={initialSolution?.global_info.total_cost}
                        b={solution.global_info.total_cost}
                        formatFn={formatCurrency}
                        lowerIsBetter
                        suffix="initial solution"
                        onlyShowDiff
                      />
                    </Text>
                    <Text size="sm">
                      {formatSeconds(solution.global_info.average_time)}{" "}
                      <DiffInfo
                        a={initialSolution?.global_info.average_time}
                        b={solution.global_info.average_time}
                        formatFn={formatSeconds}
                        lowerIsBetter
                        suffix="initial solution"
                        onlyShowDiff
                      />
                    </Text>
                    <Text size="sm">
                      {formatSeconds(solution.global_info.total_time)}{" "}
                      <DiffInfo
                        a={initialSolution?.global_info.total_time}
                        b={solution.global_info.total_time}
                        formatFn={formatSeconds}
                        lowerIsBetter
                        suffix="initial solution"
                        onlyShowDiff
                      />
                    </Text>
                    <Text size="sm">
                      {formatSeconds(solution.global_info.average_waiting_time)}{" "}
                      <DiffInfo
                        a={initialSolution?.global_info.average_waiting_time}
                        b={solution.global_info.average_waiting_time}
                        formatFn={formatSeconds}
                        lowerIsBetter
                        suffix="initial solution"
                        onlyShowDiff
                      />
                    </Text>
                    <Text size="sm">
                      {formatPercentage(
                        solution.global_info.average_resource_utilization
                      )}{" "}
                      <DiffInfo
                        a={
                          initialSolution?.global_info
                            .average_resource_utilization
                        }
                        b={solution.global_info.average_resource_utilization}
                        formatFn={formatPercentage}
                        lowerIsBetter={false}
                        suffix="initial solution"
                        onlyShowDiff
                        margin={0.01}
                      />
                    </Text>
                  </Grid.Col>
                </Grid>
              )}
            </Accordion.Panel>
          </Accordion.Item>

          <Accordion.Item value="resources">
            <Accordion.Control>Resources</Accordion.Control>
            <Accordion.Panel>
              {expanded == "resources" && (
                <ResourcesTable solution={solution} />
              )}
            </Accordion.Panel>
          </Accordion.Item>

          <Accordion.Item value="batching">
            <Accordion.Control>Batching</Accordion.Control>
            <Accordion.Panel>
              {expanded == "batching" && (
                <BatchingOverview solution={solution} />
              )}
            </Accordion.Panel>
          </Accordion.Item>

          <Accordion.Item value="actions">
            <Accordion.Control>All Modifications</Accordion.Control>
            <Accordion.Panel>
              {expanded == "actions" && (
                <ModificationOverview solution={solution} />
              )}
            </Accordion.Panel>
          </Accordion.Item>
        </Accordion>
      </Paper>
    );
  }
);
