import {
  Card,
  Grid,
  Text,
  TextInput,
  NumberInput,
  Select,
  Switch,
} from "@mantine/core";

import {
  REQUIRED_ERROR_MSG,
  SHOULD_BE_GREATER_0_MSG,
} from "../validationMessages";

import { MasterFormData } from "../hooks/useMasterFormData";
import React from "react";
import { useMasterForm, useMasterFormContext } from "../hooks/useFormContext";
import { AgentType } from "../redux/slices/optimosApi";

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
        <Grid.Col span={{ sm: 12, md: 6 }}>
          <Select
            w="100%"
            label="Approach"
            data={[
              { value: "CA", label: "CA | Calendar Only" },
              { value: "AR", label: "AR | Add/Remove Only" },
              { value: "CO", label: "CO | CA/AR combined" },
              { value: "CAAR", label: "CAAR | First CA then AR" },
              { value: "ARCA", label: "ARCA | First AR then CA" },
            ]}
            withAsterisk
            {...form.getInputProps("optimosConfig.approach")}
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
            ]}
            withAsterisk
            {...form.getInputProps("optimosConfig.agent")}
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

        <Grid.Col span={{ sm: 12, md: 12 }}>
          <Switch
            size="md"
            onLabel="OFF"
            offLabel="ON"
            label="Disable batching optimization"
            {...form.getInputProps("optimosConfig.disable_batch_optimization", {
              type: "checkbox",
            })}
          />
        </Grid.Col>
      </Grid>
    </Card>
  );
};

export default OptimosConfig;
