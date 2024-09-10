/* eslint-disable @typescript-eslint/strict-boolean-expressions */
import {
  Controller,
  useFormContext,
  type UseFormReturn,
} from "react-hook-form";

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

interface ScenarioConstraintsProps {}

const ScenarioConstraints = (props: ScenarioConstraintsProps) => {
  const { control } = useFormContext<MasterFormData>();
  const [timevar, setTimevar] = useState<number>(60);

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
            <Controller
              name="constraints.max_cap"
              control={control}
              render={({
                field: { onChange, value },
                fieldState: { error },
              }) => (
                <TextField
                  type="number"
                  value={value}
                  label="Maximum capacity"
                  onChange={(e) => {
                    onChange(Number(e.target.value));
                  }}
                  inputProps={{
                    step: "1",
                    min: "1",
                  }}
                  error={error !== undefined}
                  helperText={error?.message ?? ""}
                  variant="standard"
                  style={{ width: "50%" }}
                />
              )}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Controller
              name="constraints.max_shift_size"
              control={control}
              render={({
                field: { onChange, value },
                fieldState: { error },
              }) => (
                <TextField
                  type="number"
                  value={value}
                  label="Max shift size"
                  onChange={(e) => {
                    onChange(Number(e.target.value));
                  }}
                  inputProps={{
                    step: "1",
                    min: "1",
                    max: 1440 / timevar,
                  }}
                  error={error !== undefined}
                  helperText={error?.message ?? ""}
                  variant="standard"
                  style={{ width: "50%" }}
                />
              )}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Controller
              name="constraints.max_shift_blocks"
              control={control}
              render={({
                field: { onChange, value },
                fieldState: { error },
              }) => (
                <TextField
                  type="number"
                  value={value}
                  label="Max shifts / day"
                  onChange={(e) => {
                    onChange(Number(e.target.value));
                  }}
                  inputProps={{
                    step: "1",
                    min: "1",
                    max: 1440 / timevar,
                  }}
                  error={error !== undefined}
                  helperText={error?.message ?? ""}
                  variant="standard"
                  style={{ width: "50%" }}
                />
              )}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Controller
              name="constraints.hours_in_day"
              control={control}
              render={({
                field: { onChange, value },
                fieldState: { error },
              }) => (
                <TextField
                  style={{ display: "none" }}
                  type="hidden"
                  value={value}
                  onChange={(e) => {
                    onChange(Number(e.target.value));
                  }}
                  inputProps={{
                    step: "1",
                    min: "1",
                  }}
                  error={error !== undefined}
                  variant="standard"
                />
              )}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Controller
              name="constraints.time_var"
              control={control}
              render={({
                field: { onChange, value },
                fieldState: { error },
              }) => (
                <>
                  <InputLabel id={"time-granularity-select-label"}>
                    Time Granularity
                  </InputLabel>
                  <Select
                    required={true}
                    name="constraints.time-granularity"
                    sx={{ minWidth: 250 }}
                    labelId="time-granularity-select-label"
                    value={value}
                    label="Algorithm"
                    onChange={(e) => {
                      onChange(String(e.target.value));
                      setTimevar(Number(e.target.value));
                    }}
                    style={{ width: "50%" }}
                    error={error !== undefined}
                    variant="standard"
                  >
                    <MenuItem disabled value={"15"}>
                      15min
                    </MenuItem>
                    <MenuItem disabled value={"30"}>
                      30min
                    </MenuItem>
                    <MenuItem value={"60"}>60min</MenuItem>
                  </Select>
                </>
              )}
            />
          </Grid>
        </Grid>
      </Card>
    </>
  );
};

export default ScenarioConstraints;
