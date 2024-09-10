/* eslint-disable @typescript-eslint/strict-boolean-expressions */

import {
  Card,
  Grid,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
} from "@mui/material";
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
    <>
      <Card elevation={5} sx={{ p: 2, width: "100%" }}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Typography variant="h6" align="left">
              Global scenario constraints
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              type="number"
              label="Maximum capacity"
              slotProps={{
                htmlInput: {
                  step: "1",
                  min: "1",
                },
              }}
              variant="standard"
              style={{ width: "50%" }}
              {...form.getInputProps("constraints.max_cap")}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              type="number"
              label="Max shift size"
              inputProps={{
                step: "1",
                min: "1",
                max: 1440 / timevar,
              }}
              variant="standard"
              style={{ width: "50%" }}
              {...form.getInputProps("constraints.max_shift_size")}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              type="number"
              label="Max shifts / day"
              inputProps={{
                step: "1",
                min: "1",
                max: 1440 / timevar,
              }}
              variant="standard"
              style={{ width: "50%" }}
              {...form.getInputProps("constraints.max_shift_blocks")}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              style={{ display: "none" }}
              type="hidden"
              inputProps={{
                step: "1",
                min: "1",
              }}
              variant="standard"
              {...form.getInputProps("constraints.hours_in_day")}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <InputLabel id={"time-granularity-select-label"}>
              Time Granularity
            </InputLabel>
            <Select
              required={true}
              name="constraints.time-granularity"
              sx={{ minWidth: 250 }}
              labelId="time-granularity-select-label"
              label="Algorithm"
              style={{ width: "50%" }}
              variant="standard"
              {...form.getInputProps("constraints.time_var")}
            >
              <MenuItem disabled value={"15"}>
                15min
              </MenuItem>
              <MenuItem disabled value={"30"}>
                30min
              </MenuItem>
              <MenuItem value={"60"}>60min</MenuItem>
            </Select>
          </Grid>
        </Grid>
      </Card>
    </>
  );
};

export default ScenarioConstraints;
