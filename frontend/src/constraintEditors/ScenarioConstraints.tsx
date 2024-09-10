/* eslint-disable @typescript-eslint/strict-boolean-expressions */

import { Card, Grid, Text, NumberInput, Select } from "@mantine/core";

import {
  REQUIRED_ERROR_MSG,
  SHOULD_BE_GREATER_0_MSG,
} from "../validationMessages";
import { useState } from "react";
import type { MasterFormData } from "../hooks/useMasterFormData";
import React from "react";
import { useMasterFormContext } from "../hooks/useFormContext";

interface ScenarioConstraintsProps {}

const ScenarioConstraints = (props: ScenarioConstraintsProps) => {
  const [timevar, setTimevar] = useState<number>(60);
  const form = useMasterFormContext();

  return (
    <Card shadow="sm" padding="lg" style={{ width: "100%" }}>
      <Grid>
        <Grid.Col span={12}>
          <Text fw={500} size="lg" ta="left">
            Global scenario constraints
          </Text>
        </Grid.Col>

        <Grid.Col span={{ sm: 12, md: 6 }}>
          <NumberInput
            label="Maximum capacity"
            min={1}
            step={1}
            style={{ width: "50%" }}
            {...form.getInputProps("constraints.max_cap")}
          />
        </Grid.Col>

        <Grid.Col span={{ sm: 12, md: 6 }}>
          <NumberInput
            label="Max shift size"
            min={1}
            max={1440 / timevar}
            step={1}
            style={{ width: "50%" }}
            {...form.getInputProps("constraints.max_shift_size")}
          />
        </Grid.Col>

        <Grid.Col span={{ sm: 12, md: 6 }}>
          <NumberInput
            label="Max shifts / day"
            min={1}
            max={1440 / timevar}
            step={1}
            style={{ width: "50%" }}
            {...form.getInputProps("constraints.max_shift_blocks")}
          />
        </Grid.Col>

        <Grid.Col span={{ sm: 12, md: 6 }}>
          <input
            type="hidden"
            {...form.getInputProps("constraints.hours_in_day")}
          />
        </Grid.Col>

        <Grid.Col span={{ sm: 12, md: 6 }}>
          <Select
            label="Time Granularity"
            placeholder="Select time granularity"
            data={[
              { value: "15", label: "15min", disabled: true },
              { value: "30", label: "30min", disabled: true },
              { value: "60", label: "60min" },
            ]}
            style={{ width: "50%" }}
            {...form.getInputProps("constraints.time_var")}
          />
        </Grid.Col>
      </Grid>
    </Card>
  );
};

export default ScenarioConstraints;
