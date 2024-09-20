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
import { DiffInfo } from "./ResourceTable/ResourcesTableCell";
import {
  formatCurrency,
  formatSeconds,
  formatPercentage,
} from "../../util/num_helper";
import { ResourcesTable } from "./ResourceTable/ResourcesTable";
import { ConstraintsType } from "../../redux/slices/optimosApi";
import { useInitialSolution } from "../../hooks/useInitialSolution";
import { BatchingOverview } from "./BatchingOverview";
import { ModificationOverview } from "./ModificationOverview";

interface OptimosSolutionProps {
  solution: JSONSolution;
  finalMetrics?: any;
  constraints: ConstraintsType;
}

export const OptimosSolution: FC<OptimosSolutionProps> = memo(
  ({ finalMetrics, solution, constraints }) => {
    const initialSolution = useInitialSolution();

    const [expanded, setExpanded] = useState<string | false>(false);

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
      <Paper shadow="sm" p="md" mt="md">
        <Grid justify="space-between" align="center" style={{ height: "4em" }}>
          <Grid.Col span={8}>
            <Text size="lg" fw={500} tt="capitalize">
              {solution.isBaseSolution
                ? "Initial Solution"
                : `Solution #${solution.solutionNo}`}
            </Text>
          </Grid.Col>
          <Grid.Col span={4}>
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
            <Group>
              <Button
                onClick={() => onDownloadEntrySimParams(solution.timetable)}
                leftSection={<IconDownload />}
              >
                Parameters
              </Button>
              <Button
                onClick={() => onDownloadEntryConsParams(constraints)}
                leftSection={<IconDownload />}
              >
                Constraints
              </Button>
            </Group>
          </Grid.Col>
        </Grid>

        <Accordion defaultValue="details">
          <Accordion.Item value="details">
            <Accordion.Control>Details</Accordion.Control>
            <Accordion.Panel>
              <Grid>
                <Grid.Col span={5}>
                  <Text fw={700}>Mean cost (per case)</Text>
                  <Text fw={700}>Total cost (all cases)</Text>
                  <Text fw={700}>Mean time (per case)</Text>
                  <Text fw={700}>Total time (all cases)</Text>
                  <Text fw={700}>Mean waiting time (per case)</Text>
                  <Text fw={700}>Mean resource utilization</Text>
                </Grid.Col>
                <Grid.Col span={7}>
                  <Text>
                    {formatCurrency(solution.globalInfo.averageCost)}{" "}
                    <DiffInfo
                      a={initialSolution?.globalInfo.averageCost}
                      b={solution.globalInfo.averageCost}
                      formatFn={formatCurrency}
                      lowerIsBetter
                      suffix="initial solution"
                      onlyShowDiff
                    />
                  </Text>
                  <Text>
                    {formatCurrency(solution.globalInfo.totalCost)}{" "}
                    <DiffInfo
                      a={initialSolution?.globalInfo.totalCost}
                      b={solution.globalInfo.totalCost}
                      formatFn={formatCurrency}
                      lowerIsBetter
                      suffix="initial solution"
                      onlyShowDiff
                    />
                  </Text>
                  <Text>
                    {formatSeconds(solution.globalInfo.averageTime)}{" "}
                    <DiffInfo
                      a={initialSolution?.globalInfo.averageTime}
                      b={solution.globalInfo.averageTime}
                      formatFn={formatSeconds}
                      lowerIsBetter
                      suffix="initial solution"
                      onlyShowDiff
                    />
                  </Text>
                  <Text>
                    {formatSeconds(solution.globalInfo.totalTime)}{" "}
                    <DiffInfo
                      a={initialSolution?.globalInfo.totalTime}
                      b={solution.globalInfo.totalTime}
                      formatFn={formatSeconds}
                      lowerIsBetter
                      suffix="initial solution"
                      onlyShowDiff
                    />
                  </Text>
                  <Text>
                    {formatSeconds(solution.globalInfo.averageWaitingTime)}{" "}
                    <DiffInfo
                      a={initialSolution?.globalInfo.averageWaitingTime}
                      b={solution.globalInfo.averageWaitingTime}
                      formatFn={formatSeconds}
                      lowerIsBetter
                      suffix="initial solution"
                      onlyShowDiff
                    />
                  </Text>
                  <Text>
                    {formatPercentage(
                      solution.globalInfo.averageResourceUtilization
                    )}{" "}
                    <DiffInfo
                      a={initialSolution?.globalInfo.averageResourceUtilization}
                      b={solution.globalInfo.averageResourceUtilization}
                      formatFn={formatPercentage}
                      lowerIsBetter={false}
                      suffix="initial solution"
                      onlyShowDiff
                      margin={0.01}
                    />
                  </Text>
                </Grid.Col>
              </Grid>
            </Accordion.Panel>
          </Accordion.Item>

          <Accordion.Item value="resources">
            <Accordion.Control>Resources</Accordion.Control>
            <Accordion.Panel>
              <ResourcesTable solution={solution} />
            </Accordion.Panel>
          </Accordion.Item>

          <Accordion.Item value="batching">
            <Accordion.Control>Batching</Accordion.Control>
            <Accordion.Panel>
              <BatchingOverview solution={solution} />
            </Accordion.Panel>
          </Accordion.Item>

          <Accordion.Item value="actions">
            <Accordion.Control>value="All Modifications"</Accordion.Control>
            <Accordion.Panel>
              <ModificationOverview solution={solution} />
            </Accordion.Panel>
          </Accordion.Item>
        </Accordion>
      </Paper>
    );
  }
);
