import {
  Card,
  Grid,
  Text,
  TextInput,
  NumberInput,
  Select,
} from "@mantine/core";

import {
  REQUIRED_ERROR_MSG,
  SHOULD_BE_GREATER_0_MSG,
} from "../validationMessages";

import { MasterFormData } from "../hooks/useMasterFormData";
import React from "react";
import { useMasterForm, useMasterFormContext } from "../hooks/useFormContext";

interface GlobalConstraintsProps {}

const GlobalConstraints = (props: GlobalConstraintsProps) => {
  const form = useMasterFormContext();
  return (
    <Card shadow="sm" padding="lg" style={{ width: "100%" }}>
      <Grid justify="flex-start">
        <Grid.Col span={12}>
          <Text fw={500} size="lg" ta="left">
            Scenario specification
          </Text>
        </Grid.Col>

        <Grid.Col span={6}>
          <TextInput
            label="Scenario name"
            withAsterisk
            style={{ width: "75%" }}
            {...form.getInputProps("scenarioProperties.scenario_name")}
          />
        </Grid.Col>

        <Grid.Col span={6}>
          <NumberInput
            label="Total number of iterations"
            min={1}
            step={1}
            withAsterisk
            style={{ width: "75%" }}
            {...form.getInputProps("scenarioProperties.num_instances")}
          />
        </Grid.Col>

        <Grid.Col span={6}>
          <Select
            label="Approach"
            data={[
              { value: "CA", label: "CA | Calendar Only" },
              { value: "AR", label: "AR | Add/Remove Only" },
              { value: "CO", label: "CO | CA/AR combined" },
              { value: "CAAR", label: "CAAR | First CA then AR" },
              { value: "ARCA", label: "ARCA | First AR then CA" },
            ]}
            withAsterisk
            style={{ minWidth: 250 }}
            {...form.getInputProps("scenarioProperties.approach")}
          />
        </Grid.Col>
      </Grid>
    </Card>
  );
};

export default GlobalConstraints;
