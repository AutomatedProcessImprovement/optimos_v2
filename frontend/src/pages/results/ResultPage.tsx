import {
  Button,
  Group,
  Grid,
  Paper,
  Text,
  Loader,
  Accordion,
  Box,
} from "@mantine/core";
import { IconDownload, IconX } from "@tabler/icons-react";
import React, { FC, useCallback, useEffect, useRef, useState } from "react";
import { ProcessingRequest } from "../../redux/slices/optimosApi";
import { OptimosSolution } from "./Solution";
import { SolutionChart } from "./SolutionChart";
import { useReport } from "../../hooks/useReport";

const OptimizationResults: FC = () => {
  const [report, loading, error] = useReport();

  const [fileDownloadUrl, setFileDownloadUrl] = useState("");

  const linkDownloadRef = useRef<HTMLAnchorElement>(null);

  useEffect(() => {
    if (fileDownloadUrl) {
      linkDownloadRef.current?.click();
      URL.revokeObjectURL(fileDownloadUrl);
    }
  }, [fileDownloadUrl]);

  const onDownload = () => {
    if (!report) return;
    const blob = new Blob([JSON.stringify(report)], {
      type: "application/json",
    });
    const optimizationReportFile = new File([blob], "name", {
      type: "application/json",
    });
    const fileDownloadUrl = URL.createObjectURL(optimizationReportFile);
    setFileDownloadUrl(fileDownloadUrl);
  };

  const onCancel = useCallback(async () => {
    // TODO Cancel
  }, []);

  if (!report || loading || !report.pareto_fronts) {
    return (
      <Grid
        justify="center"
        ta="center"
        style={{ height: "100vh", flexDirection: "column" }}
      >
        <Loader size={50} />
        <Text size="lg">Loading...</Text>
      </Grid>
    );
  }

  const lastParetoFront = report.pareto_fronts[report.pareto_fronts.length - 1];
  const all_but_last_pareto_front = report.pareto_fronts.slice(0, -1);
  const final_metrics = {
    ave_cost: 0,
    ave_time: 0,
    cost_metric: 0,
    time_metric: 0,
  };

  return (
    <Grid pt="50px" ta="center" justify="center" style={{ paddingTop: "10px" }}>
      <Grid.Col span={8}>
        <Grid>
          <Grid.Col span={12}>
            <h1 className="text-3xl font-semibold">Your Optimization Report</h1>
          </Grid.Col>
          <Grid.Col span={12}>
            <Paper shadow="sm" p="md">
              <Grid>
                <Grid.Col span={8}>
                  <Text size="lg">{report.name}</Text>
                </Grid.Col>
                <Grid.Col span={4} style={{ textAlign: "right" }}>
                  <Group>
                    {!report.isFinal && (
                      <Button
                        variant="outline"
                        color="red"
                        leftSection={<IconX />}
                        onClick={onCancel}
                      >
                        Cancel
                      </Button>
                    )}
                    <Button
                      variant="filled"
                      onClick={onDownload}
                      leftSection={<IconDownload />}
                    >
                      Report
                    </Button>
                  </Group>
                  <a
                    style={{ display: "none" }}
                    download="report.json"
                    href={fileDownloadUrl}
                    ref={linkDownloadRef}
                  >
                    Download json
                  </a>
                </Grid.Col>
                <Grid.Col span={12}>
                  <Grid justify="center">
                    <Loader size={60} />
                  </Grid>
                  <Grid justify="center" mb="md">
                    <Text ta="center">
                      The Process is still running, below you find the current
                      iteration
                    </Text>
                  </Grid>
                  <SolutionChart
                    optimalSolutions={lastParetoFront.solutions.filter(
                      (sol) => !sol.isBaseSolution
                    )}
                    otherSolutions={all_but_last_pareto_front
                      .flatMap((front) => front.solutions)
                      .filter((sol) => !sol.isBaseSolution)}
                  />
                </Grid.Col>
              </Grid>
            </Paper>
            <Grid>
              {lastParetoFront.solutions.map((solution, index) => (
                <Grid.Col
                  span={12}
                  key={`grid-${index}`}
                  id={`solution_${index}`}
                >
                  <OptimosSolution
                    key={index}
                    solution={solution}
                    finalMetrics={final_metrics}
                    constraints={report.constraints}
                  />
                </Grid.Col>
              ))}
              {!!all_but_last_pareto_front.length && (
                <>
                  <Grid.Col id="non-optimal-solutions">
                    <Text size="lg" fw={500}>
                      Previous (non-optimal) solutions
                    </Text>
                  </Grid.Col>
                  <Grid.Col span={12} my="md">
                    <Accordion>
                      <Accordion.Item value="initialSolution">
                        <Accordion.Control>Initial Solution</Accordion.Control>
                        <Accordion.Panel>
                          <OptimosSolution
                            solution={report.baseSolution}
                            constraints={report.constraints}
                          />
                        </Accordion.Panel>
                      </Accordion.Item>

                      {all_but_last_pareto_front.map((front, index) => (
                        <Accordion.Item
                          value={`non-optimal-solution-chunk-${index}`}
                          key={`non-optimal-solution-chunk-${index}`}
                        >
                          <Accordion.Control>
                            Solution-Group ${index + 1}
                          </Accordion.Control>
                          <Accordion.Panel>
                            <Grid>
                              {front.solutions.map((solution, index) => (
                                <Grid.Col
                                  span={12}
                                  key={`grid-${index}`}
                                  id={`solution_${index}`}
                                >
                                  <OptimosSolution
                                    key={index}
                                    solution={solution}
                                    finalMetrics={final_metrics}
                                    constraints={report.constraints}
                                  />
                                </Grid.Col>
                              ))}
                            </Grid>
                          </Accordion.Panel>
                        </Accordion.Item>
                      ))}
                    </Accordion>
                  </Grid.Col>
                </>
              )}
            </Grid>
          </Grid.Col>
        </Grid>
      </Grid.Col>
    </Grid>
  );
};

export default OptimizationResults;
