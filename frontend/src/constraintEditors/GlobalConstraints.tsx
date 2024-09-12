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
      <Grid justify="flex-start" ta="left">
        <Grid.Col span={12}>
          <Text fw={500} size="lg">
            Scenario specification
          </Text>
        </Grid.Col>

        <Grid.Col span={{ sm: 12, md: 6 }}>
          <TextInput
            label="Scenario name"
            withAsterisk
            w="75%"
            {...form.getInputProps("scenarioProperties.scenario_name")}
          />
          <Select
            my="sm"
            w="75%"
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

        <Grid.Col span={{ sm: 12, md: 6 }}>
          <NumberInput
            label="Total number of iterations"
            min={1}
            step={1}
            withAsterisk
            w="75%"
            {...form.getInputProps("scenarioProperties.num_instances")}
          />
        </Grid.Col>
      </Grid>
    </Card>
  );
};

export default GlobalConstraints;
