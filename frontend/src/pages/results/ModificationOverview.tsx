import { Card, Grid, Text, Group } from "@mantine/core";
import type { FC } from "react";
import {
  IconCirclePlus,
  IconCopy,
  IconArrowRight,
  IconCircleMinus,
  IconTrash,
} from "@tabler/icons-react";
import React from "react";
import { JsonAction, JsonSolution } from "../../redux/slices/optimosApi";
import { TaskNameDisplay } from "../../components/TaskNameDisplay";

type ModificationOverviewProps = {
  solution: JsonSolution;
};

export const ModificationOverview: FC<ModificationOverviewProps> = (props) => {
  const { solution } = props;
  const actions = solution.actions;

  return (
    <Grid>
      {actions.length == 0 && (
        <Text size="lg" fw={500}>
          No modifications so far.
        </Text>
      )}
      {actions.map((action, index) => {
        return (
          <Grid.Col span={{ md: 6, lg: 4, xl: 3 }} key={index}>
            <ActionCard action={action} />
          </Grid.Col>
        );
      })}
    </Grid>
  );
};

const ActionCard = ({ action }: { action: JsonAction }) => {
  let title;
  let description;
  let icon;

  switch (action.type) {
    case "AddResourceAction":
      icon = <IconCopy size={16} />;
      title = "Clone Resource";
      description = (
        <span>
          Cloned resource <b>{action.params["resource_id"]}.</b>
        </span>
      );
      break;
    case "ModifyCalendarByCostAction":
    case "ModifyCalendarByITAction":
    case "ModifyCalendarByWTAction":
      const resourceId = action.params["calendar_id"].replace("timetable", "");
      if ("shift_hours" in action.params) {
        icon = <IconArrowRight size={16} />;
        title = `Move shift to start${
          action.params["shift_hours"] > 0 ? " later" : " earlier"
        }`;
        description = (
          <span>
            Moved <b>shift "{action.params["period_id"]}"</b> on{" "}
            <b>{action.params["day"]}</b> by {action.params["shift_hours"]}{" "}
            hours for resource <b>{resourceId}</b>.
          </span>
        );
      } else if (
        "add_hours_after" in action.params &&
        "add_hours_before" in action.params
      ) {
        if (
          action.params["add_hours_after"] > 0 &&
          action.params["add_hours_before"] > 0
        ) {
          icon = <IconCirclePlus size={16} />;
          title = "Add hours before and after shift";
          description = (
            <span>
              Added {action.params["add_hours_before"]} hours before and{" "}
              {action.params["add_hours_after"]} hours after{" "}
              <b>shift "{action.params["period_id"]}"</b> on{" "}
              <b>{action.params["day"]}</b> for resource <b>{resourceId}</b>.
            </span>
          );
        } else if (
          action.params["add_hours_after"] < 0 &&
          action.params["add_hours_before"] < 0
        ) {
          icon = <IconCircleMinus size={16} />;
          title = "Remove hours before and after shift";
          description = (
            <span>
              Removed {Math.abs(action.params["add_hours_before"])} hours before
              and {Math.abs(action.params["add_hours_after"])} hours after{" "}
              <b>shift "{action.params["period_id"]}"</b> on{" "}
              <b>{action.params["day"]}</b> for resource <b>{resourceId}</b>.
            </span>
          );
        }
      } else if (
        "add_hours_after" in action.params &&
        action.params["add_hours_after"] > 0
      ) {
        icon = <IconCirclePlus size={16} />;
        title = "Add hours after shift";
        description = (
          <span>
            Added {action.params["add_hours_after"]} hours after{" "}
            <b>shift "{action.params["period_id"]}"</b> on{" "}
            <b>{action.params["day"]}</b> for resource <b>{resourceId}</b>.
          </span>
        );
      } else if (
        "add_hours_after" in action.params &&
        action.params["add_hours_after"] < 0
      ) {
        icon = <IconCircleMinus size={16} />;
        title = "Remove hours after shift";
        description = (
          <span>
            Removed {Math.abs(action.params["add_hours_after"])} hours after{" "}
            <b>shift "{action.params["period_id"]}"</b> on{" "}
            <b>{action.params["day"]}</b> for resource <b>{resourceId}</b>.
          </span>
        );
      } else if (
        "add_hours_before" in action.params &&
        action.params["add_hours_before"] > 0
      ) {
        icon = <IconCirclePlus size={16} />;
        title = "Add hours before shift";
        description = (
          <span>
            Added {action.params["add_hours_before"]} hours before{" "}
            <b>shift "{action.params["period_id"]}"</b> on{" "}
            <b>{action.params["day"]}</b> for resource <b>{resourceId}</b>.
          </span>
        );
      } else if (
        "add_hours_before" in action.params &&
        action.params["add_hours_before"] < 0
      ) {
        icon = <IconCircleMinus size={16} />;
        title = "Remove hours before shift";
        description = (
          <span>
            Removed {Math.abs(action.params["add_hours_before"])} hours before{" "}
            <b>shift "{action.params["period_id"]}"</b> on{" "}
            <b>{action.params["day"]}</b> for resource <b>{resourceId}</b>.
          </span>
        );
      } else if ("remove_period" in action.params) {
        icon = <IconTrash size={16} />;
        title = "Remove shift";
        description = (
          <span>
            Removed <b>shift "{action.params["period_id"]}"</b> on{" "}
            <b>{action.params["day"]}</b> for resource <b>{resourceId}</b>.
          </span>
        );
      }
      break;
    case "RemoveResourceByUtilizationAction":
      icon = <IconTrash size={16} />;
      title = "Remove Resource";
      description = (
        <span>
          Removed resource <b>{action.params["resource_id"]}.</b>
        </span>
      );
      break;
    case "AddDateTimeRuleAction":
    case "AddDateTimeRuleByAvailabilityAction":
    case "AddDateTimeRuleByStartAction":
    case "AddDateTimeRuleByEnablementAction":
      icon = <IconCirclePlus size={16} />;
      const ruleType =
        action.type === "AddDateTimeRuleAction"
          ? ""
          : action.type === "AddDateTimeRuleByAvailabilityAction"
          ? "based on availability"
          : action.type === "AddDateTimeRuleByStartAction"
          ? "based on start time"
          : "based on enablement";
      title = `Add Date Time Rule${
        ruleType ? ` by ${ruleType.split(" ")[2]}` : ""
      }`;
      description = (
        <span>
          Added date time rule {ruleType} for{" "}
          <b>
            <TaskNameDisplay taskId={action.params["task_id"]} />
          </b>{" "}
          on <b>{action.params["time_period"]["from_"]}</b> from{" "}
          <b>{action.params["time_period"]["begin_time"]}</b> to{" "}
          <b>{action.params["time_period"]["end_time"]}</b>.
        </span>
      );
      break;
    case "AddReadyLargeWTRuleAction":
      icon = <IconCirclePlus size={16} />;
      title = "Add Ready Large WT Rule";
      description = (
        <span>
          Added ready large WT rule for <b>{action.params["rule"]}.</b>
        </span>
      );
      break;
    case "AddSizeRuleAction":
      icon = <IconCirclePlus size={16} />;
      title = "Add Size Rule";
      description = (
        <span>
          Added size rule with size <b>{action.params["size"]}</b> for task{" "}
          <b>
            <TaskNameDisplay taskId={action.params["task_id"]} />
          </b>
          .
        </span>
      );
      break;
    case "ModifyDailyHourRuleAction":
      icon = <IconArrowRight size={16} />;
      title = "Modify Daily Hour Rule";
      description = (
        <span>
          Modified daily hour rule for{" "}
          <b>{getRuleDisplayText(action.params["rule"])}</b>.
        </span>
      );
      break;
    case "ModifySizeRuleAction":
    case "ModifySizeRuleByCostAction":
    case "ModifySizeRuleByUtilizationAction":
    case "ModifySizeRuleByDurationFnCostImpactAction":
    case "ModifyBatchSizeIfNoDurationImprovementAction":
    case "ModifySizeRuleByLowAllocationAction":
    case "ModifySizeRuleByHighAllocationAction":
    case "ModifySizeRuleByWTAction":
    case "ModifySizeRuleByCostFnRepetitiveTasksAction":
    case "ModifySizeRuleByCostFnHighCostsAction":
    case "ModifySizeRuleByCostFnLowProcessingTimeAction":
    case "ModifyBatchSizeIfNoCostImprovementAction":
    case "ModifySizeRuleByCostFnLowCycleTimeImpactAction":
    case "ModifySizeRuleByManySimilarEnablementsAction":
      icon = <IconArrowRight size={16} />;
      title =
        action.params["size_increment"] > 0
          ? "Increase Size Rule"
          : "Decrease Size Rule";
      description = (
        <span>
          {action.params["size_increment"] > 0 ? "Increased" : "Decreased"} size
          rule by <b>{Math.abs(action.params["size_increment"])}</b> for task{" "}
          <b>{getRuleDisplayText(action.params["rule"])}</b>.
        </span>
      );
      break;
    case "RemoveRuleAction":
      icon = <IconTrash size={16} />;
      title = "Remove Rule";
      description = (
        <span>
          Removed rule <b>{getRuleDisplayText(action.params["rule"])}</b>.
        </span>
      );
      break;
    case "ModifyReadyWtRuleAction":
      icon = <IconArrowRight size={16} />;
      title =
        action.params["wt_increment"] > 0
          ? "Increase Ready WT Rule"
          : "Decrease Ready WT Rule";
      description = (
        <span>
          {action.params["wt_increment"] > 0 ? "Increased" : "Decreased"} ready
          WT rule by <b>{Math.abs(action.params["wt_increment"])}</b> for task{" "}
          <b>{getRuleDisplayText(action.params["rule"])}</b>.
        </span>
      );
      break;
    case "ModifyLargeWtRuleAction":
      icon = <IconArrowRight size={16} />;
      title =
        action.params["wt_increment"] > 0
          ? "Increase Large WT Rule"
          : "Decrease Large WT Rule";
      description = (
        <span>
          {action.params["wt_increment"] > 0 ? "Increased" : "Decreased"} large
          WT rule by <b>{Math.abs(action.params["wt_increment"])}</b> for task{" "}
          <b>{getRuleDisplayText(action.params["rule"])}</b>.
        </span>
      );
      break;
    case "ModifySizeOfSignificantRuleAction":
      icon = <IconArrowRight size={16} />;
      title =
        action.params["size_increment"] > 0
          ? "Increase Size of Significant Rule"
          : "Decrease Size of Significant Rule";
      description = (
        <span>
          {action.params["size_increment"] > 0 ? "Increased" : "Decreased"} size
          of significant rule by{" "}
          <b>{Math.abs(action.params["size_increment"])}</b> for task{" "}
          <b>{getRuleDisplayText(action.params["rule"])}</b>.
        </span>
      );
      break;
    case "ModifyLargeReadyWtOfSignificantRuleAction":
      icon = <IconArrowRight size={16} />;
      title =
        action.params["wt_increment"] > 0
          ? "Increase Large Ready WT of Significant Rule"
          : "Decrease Large Ready WT of Significant Rule";
      description = (
        <span>
          {action.params["wt_increment"] > 0 ? "Increased" : "Decreased"} large
          ready WT of significant rule by{" "}
          <b>{Math.abs(action.params["wt_increment"])}</b> for task{" "}
          <b>{getRuleDisplayText(action.params["rule"])}</b>.
        </span>
      );
      break;
    case "RemoveResourceByCostAction":
      icon = <IconTrash size={16} />;
      title = "Remove Resource by Cost";
      description = (
        <span>
          Removed resource <b>{action.params["resource_id"]}</b> based on cost.
        </span>
      );
      break;
    case "ShiftDateTimeRuleAction":
      icon = <IconArrowRight size={16} />;
      title = "Shift Date Time Rule";
      description = (
        <span>
          Shifted date time rule for{" "}
          <b>
            <TaskNameDisplay taskId={action.params["task_id"]} />
          </b>{" "}
          on <b>{action.params["day"]}</b> by{" "}
          <b>{action.params["add_to_start"]}</b> hours at start and{" "}
          <b>{action.params["add_to_end"]}</b> hours at end.
        </span>
      );
      break;
    case "RemoveDateTimeRuleAction":
      icon = <IconTrash size={16} />;
      title = "Remove Date Time Rule";
      description = (
        <span>
          Removed date time rule for{" "}
          <b>
            <TaskNameDisplay taskId={action.params["task_id"]} />
          </b>{" "}
          on <b>{action.params["day"]}</b>.
        </span>
      );
      break;
    case "AddReadyWTRuleByWTAction":
    case "AddLargeWTRuleByWTAction":
    case "AddLargeWTRuleByIdleAction":
      icon = <IconCirclePlus size={16} />;
      title =
        action.type === "AddReadyWTRuleByWTAction"
          ? "Add Ready WT Rule"
          : "Add Large WT Rule";
      description = (
        <span>
          Added {action.type === "AddReadyWTRuleByWTAction" ? "ready" : "large"}{" "}
          WT rule with waiting time <b>{action.params["wt"]}</b>{" "}
          {action.type === "AddLargeWTRuleByIdleAction"
            ? "based on idle time"
            : ""}{" "}
          for task{" "}
          <b>
            <TaskNameDisplay taskId={action.params["task_id"]} />
          </b>
          .
        </span>
      );
      break;
    default:
      console.warn("Unknown action type", action);
      title = "Unknown action";
      description = "Unknown action type";
  }

  return (
    <Card>
      <Group align="center" gap="xs" p="1rem">
        {icon}
        <Text size="lg" fw={500}>
          {title}
        </Text>
      </Group>
      <Text size="sm" px="1rem">
        {description}
      </Text>
    </Card>
  );
};

const getRuleDisplayText = (rule: any): React.ReactNode => {
  if (!rule) return "Unknown";
  if (typeof rule === "string") return rule;
  if (typeof rule === "object") {
    if (rule.batching_rule_task_id)
      return <TaskNameDisplay taskId={rule.batching_rule_task_id} />;
    if (rule.task_id) return <TaskNameDisplay taskId={rule.task_id} />;
    if (rule.id) return <TaskNameDisplay taskId={rule.id} />;
    return "Unknown Rule";
  }
  return "Unknown";
};
