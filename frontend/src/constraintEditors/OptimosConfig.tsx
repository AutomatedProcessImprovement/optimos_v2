import {
  Card,
  Grid,
  Text,
  TextInput,
  NumberInput,
  Select,
  Switch,
  SegmentedControl,
  Center,
  Spoiler,
} from "@mantine/core";

import {
  REQUIRED_ERROR_MSG,
  SHOULD_BE_GREATER_0_MSG,
} from "../validationMessages";

import { MasterFormData } from "../hooks/useMasterFormData";
import React from "react";
import { useMasterForm, useMasterFormContext } from "../hooks/useFormContext";
import {
  ActionVariationSelection,
  AgentType,
  CostType,
  LegacyApproachAbbreviation,
  Mode,
} from "../redux/slices/optimosApi";
import { IconCalendarWeek, IconCategoryPlus } from "@tabler/icons-react";
import { unsnakecase } from "../helpers";

const ACTION_VARIATION_DESCRIPTIONS = {
  [ActionVariationSelection.SingleRandom]: "Try a single random variation",
  [ActionVariationSelection.FirstInOrder]: "Try the first variation generated",
  [ActionVariationSelection.FirstMaxVariantsPerActionInOrder]:
    "Try the first n variations as configured in 'Max. number of variations per action'",
  [ActionVariationSelection.RandomMaxVariantsPerAction]:
    "Try n random variations, as configured in 'Max. number of variations per action'",
  [ActionVariationSelection.AllRandom]: "Try all variations randomly",
  [ActionVariationSelection.AllInOrder]: "Try all variations in order",
};

const COST_TYPE_LABEL = {
  [CostType.TotalCost]: "Resource + Fixed Cost",
  [CostType.ResourceCost]: "Resource Cost",
  [CostType.FixedCost]: "Fixed Cost",
  [CostType.WtPt]: "Waiting Time + Processing Time",
  [CostType.AvgWtPtPerTaskInstance]:
    "Avg. Waiting Time + Processing Time per Task Instance",
};

const COST_TYPE_DESCRIPTIONS = {
  [CostType.TotalCost]: "Resource cost + Fixed cost",
  [CostType.ResourceCost]: "Resource cost",
  [CostType.FixedCost]: "Fixed cost",
  [CostType.WtPt]: "Total Waiting time + Processing time",
  [CostType.AvgWtPtPerTaskInstance]:
    "Average Waiting time + Processing time per task instance",
};

interface OptimosConfigProps {}

const OptimosConfig = (props: OptimosConfigProps) => {
  const form = useMasterFormContext();
  return (
    <Card shadow="sm" padding="lg" style={{ width: "100%" }}>
      <Grid justify="flex-start" ta="left" align="flex-start">
        <Grid.Col span={12}>
          <Text fw={500} size="lg">
            Scenario specification
          </Text>
        </Grid.Col>

        <Grid.Col span={{ sm: 12, md: 12 }}>
          <TextInput
            label="Scenario name"
            withAsterisk
            w="100%"
            {...form.getInputProps("optimosConfig.scenario_name")}
          />
        </Grid.Col>
        <Grid.Col span={12}>
          <SegmentedControl
            fullWidth
            data={[
              {
                value: "batching",
                label: (
                  <Center style={{ gap: 10 }}>
                    <IconCategoryPlus size={16} />
                    <span>Batching Optimization</span>
                  </Center>
                ),
              },
              {
                value: "calendar",
                label: (
                  <Center style={{ gap: 10 }}>
                    <IconCalendarWeek size={16} />
                    <span>Calendar Optimization</span>
                  </Center>
                ),
              },
            ]}
            {...form.getInputProps("optimosConfig.mode")}
          />
        </Grid.Col>

        <Grid.Col span={{ sm: 12, md: 6 }}>
          <Select
            w="100%"
            label="Approach"
            placeholder="No approach for batch optimization"
            data={
              form.values?.optimosConfig?.mode === "calendar"
                ? [
                    { value: "CA", label: "CA | Calendar Only" },
                    { value: "AR", label: "AR | Add/Remove Only" },
                    { value: "CO", label: "CO | CA/AR combined" },
                    { value: "CAAR", label: "CAAR | First CA then AR" },
                    { value: "ARCA", label: "ARCA | First AR then CA" },
                  ]
                : []
            }
            disabled={form.values?.optimosConfig?.mode === Mode.Batching}
            withAsterisk
            {...form.getInputProps("optimosConfig.approach")}
            value={
              form.values?.optimosConfig?.mode === Mode.Batching
                ? null
                : form.values?.optimosConfig?.approach
            }
          />
        </Grid.Col>

        <Grid.Col span={{ sm: 12, md: 6 }}>
          <Select
            w="100%"
            label="Agent"
            data={[
              { value: AgentType.TabuSearch, label: "Tabu Search" },
              {
                value: AgentType.SimulatedAnnealing,
                label: "Simulated Annealing",
              },
              { value: AgentType.ProximalPolicyOptimization, label: "PPO" },
              {
                value: AgentType.TabuSearchRandom,
                label: "Tabu Search Random",
              },
              {
                value: AgentType.SimulatedAnnealingRandom,
                label: "Simulated Annealing Random",
              },
              {
                value: AgentType.ProximalPolicyOptimizationRandom,
                label: "PPO Random",
              },
            ]}
            withAsterisk
            {...form.getInputProps("optimosConfig.agent")}
          />
        </Grid.Col>

        <Grid.Col span={{ sm: 12, md: 6 }}>
          <Select
            w="100%"
            label="Cost Function"
            data={Object.values(CostType).map((value) => ({
              value,
              label: COST_TYPE_LABEL[value],
            }))}
            renderOption={({ option }) => (
              <div>
                <Text fz="sm" fw={500}>
                  {option.label}
                </Text>
                <Text fz="xs" c="dimmed">
                  {COST_TYPE_DESCRIPTIONS[option.value]}
                </Text>
              </div>
            )}
            {...form.getInputProps("optimosConfig.cost_type")}
          />
        </Grid.Col>

        <Grid.Col span={{ sm: 12, md: 6 }}>
          <NumberInput
            label="Cases per simulation"
            min={1}
            step={1}
            withAsterisk
            w="100%"
            {...form.getInputProps("optimosConfig.num_cases")}
          />
        </Grid.Col>

        <Grid.Col span={{ sm: 12, md: 6 }}>
          <NumberInput
            label="Max. actions per iteration"
            placeholder="auto"
            min={1}
            step={1}
            w="100%"
            {...form.getInputProps("optimosConfig.max_actions_per_iteration")}
          />
        </Grid.Col>

        <Grid.Col span={{ sm: 12, md: 6 }}>
          <Select
            w="100%"
            label="Action variation selection"
            data={Object.values(ActionVariationSelection).map((value) => ({
              value,
              label: unsnakecase(value),
            }))}
            renderOption={({ option }) => (
              <div>
                <Text fz="sm" fw={500}>
                  {option.label}
                </Text>
                <Text fz="xs" c="dimmed">
                  {ACTION_VARIATION_DESCRIPTIONS[option.value]}
                </Text>
              </div>
            )}
            {...form.getInputProps("optimosConfig.action_variation_selection")}
          />
        </Grid.Col>

        <Grid.Col span={{ sm: 12, md: 6 }}>
          <NumberInput
            label="Max. number of variations per action"
            placeholder="auto"
            min={1}
            step={1}
            w="100%"
            {...form.getInputProps(
              "optimosConfig.max_number_of_variations_per_action"
            )}
          />
        </Grid.Col>

        {form.values?.optimosConfig?.agent === AgentType.SimulatedAnnealing && (
          <Grid.Col span={{ sm: 12, md: 6 }}>
            <Text fw={500} size="sm">
              Simulated Annealing: Solution Order
            </Text>
            <SegmentedControl
              data={[
                { value: "random", label: "Random" },
                { value: "greedy", label: "Greedy" },
              ]}
              fullWidth
              {...form.getInputProps("optimosConfig.sa_solution_order")}
            />
          </Grid.Col>
        )}

        {form.values?.optimosConfig?.agent === AgentType.SimulatedAnnealing && (
          <Grid.Col span={{ sm: 12, md: 6 }}>
            <NumberInput
              label="Simulated Annealing: Initial Temperature"
              placeholder="auto"
              min={1}
              step={1}
              w="100%"
              {...form.getInputProps("optimosConfig.sa_temperature")}
            />
          </Grid.Col>
        )}

        {form.values?.optimosConfig?.agent === AgentType.SimulatedAnnealing && (
          <Grid.Col span={{ sm: 12, md: 6 }}>
            <NumberInput
              label="Simulated Annealing: Cooling rate"
              placeholder="auto"
              min={1}
              step={1}
              w="100%"
              {...form.getInputProps("optimosConfig.sa_cooling_rate")}
            />
          </Grid.Col>
        )}

        <Grid.Col span={{ sm: 12, md: 6 }}>
          <NumberInput
            label="Max. number of solutions"
            placeholder="auto"
            min={1}
            step={1}
            w="100%"
            {...form.getInputProps("optimosConfig.max_solutions")}
          />
        </Grid.Col>

        <Grid.Col span={{ sm: 12, md: 6 }}>
          <NumberInput
            label="Max. non-improving actions"
            min={1}
            step={1}
            withAsterisk
            w="100%"
            {...form.getInputProps("optimosConfig.max_non_improving_actions")}
          />
        </Grid.Col>
        <Grid.Col span={{ sm: 12, md: 6 }}>
          <NumberInput
            label="Max. iterations"
            min={1}
            step={1}
            withAsterisk
            w="100%"
            {...form.getInputProps("optimosConfig.max_iterations")}
          />
        </Grid.Col>
      </Grid>
    </Card>
  );
};

export default OptimosConfig;
