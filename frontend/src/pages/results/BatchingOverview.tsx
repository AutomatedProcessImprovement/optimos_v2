import React from "react";
import { Grid, Text, Accordion, Box } from "@mantine/core";
import { Tree } from "react-d3-tree";
import { FC } from "react";
import {
  BatchingRule,
  JsonSolution,
  RULE_TYPE,
  COMPARATOR,
} from "../../redux/slices/optimosApi";
import { useInitialSolution } from "../../hooks/useInitialSolution";
import { formatSeconds } from "../../util/num_helper";
import { DiffInfo } from "./ResourceTable/DiffInfo";
import { TaskNameDisplay } from "../../components/TaskNameDisplay";
import { useTaskNames } from "../../hooks/useTaskNames";

const getReadableLabel = (
  attribute: RULE_TYPE,
  comparison: COMPARATOR,
  value: string | number
) => {
  const attributeMap: Record<RULE_TYPE, string> = {
    [RULE_TYPE.ReadyWt]: "Ready Waiting Time",
    [RULE_TYPE.LargeWt]: "Large Waiting Time",
    [RULE_TYPE.Size]: "Batch Size",
    [RULE_TYPE.WeekDay]: "Week Day",
    [RULE_TYPE.DailyHour]: "Daily Hour",
  };

  const comparisonMap: Record<string, string> = {
    "<=": "≤",
    ">=": "≥",
    ">": ">",
    "<": "<",
    "=": "=",
  };

  const readableAttribute = attributeMap[attribute];
  const readableComparison = comparisonMap[comparison];

  // Format the value based on the attribute type
  let formattedValue = value;
  if (attribute === RULE_TYPE.ReadyWt || attribute === RULE_TYPE.LargeWt) {
    formattedValue = formatSeconds(Number(value));
  }

  return `${readableAttribute} ${readableComparison} ${formattedValue}`;
};

const transformBatchingRulesToTree = (rule: BatchingRule) => {
  const taskNames = useTaskNames();
  const taskName = taskNames[rule.task_id] ?? rule.task_id;
  const root = {
    name: `Task: ${taskName}`,
    children: rule.firing_rules.map((orRule, index) => ({
      name: `OR Rule ${index + 1}`,
      children: orRule.map((andRule) => ({
        name: getReadableLabel(
          andRule.attribute,
          andRule.comparison,
          andRule.value
        ),
      })),
    })),
  };
  return root;
};

export const BatchingOverview = ({ solution }: { solution: JsonSolution }) => {
  const initialSolution = useInitialSolution();
  const batchingRules = solution.timetable.batch_processing || [];

  return (
    <Grid>
      <Grid.Col span={5}>
        <Text fw={700} ta="left">
          Waiting time due to batching
        </Text>
      </Grid.Col>
      <Grid.Col span={7}>
        <Text ta="left">
          {formatSeconds(solution.global_info.total_cost)}{" "}
          <DiffInfo
            a={initialSolution?.global_info.total_cost}
            b={solution.global_info.total_cost}
            formatFn={formatSeconds}
            lowerIsBetter
            suffix="initial solution"
            onlyShowDiff
            margin={0.0}
          />
        </Text>
      </Grid.Col>
      <Grid.Col span={12}>
        <Accordion>
          {batchingRules.map((rule, index) => (
            <Accordion.Item key={index} value={`rule-${index}`}>
              <Accordion.Control>
                <Text fw={500}>
                  Task: <TaskNameDisplay taskId={rule.task_id} />
                </Text>
              </Accordion.Control>
              <Accordion.Panel>
                <Box style={{ height: "300px", width: "100%" }}>
                  <Tree
                    data={transformBatchingRulesToTree(rule)}
                    orientation="vertical"
                    pathFunc="step"
                    translate={{ x: 200, y: 50 }}
                    separation={{ siblings: 2, nonSiblings: 2 }}
                    nodeSize={{ x: 200, y: 100 }}
                    zoom={0.8}
                  />
                </Box>
              </Accordion.Panel>
            </Accordion.Item>
          ))}
        </Accordion>
      </Grid.Col>
    </Grid>
  );
};
