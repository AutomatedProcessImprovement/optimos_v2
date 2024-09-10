import {
  Controller,
  useController,
  useFormContext,
  useFormState,
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

import { MasterFormData } from "../hooks/useMasterFormData";
import React from "react";

interface GlobalConstraintsProps {}

const GlobalConstraints = (props: GlobalConstraintsProps) => {
  const { control } = useFormContext<MasterFormData>();
  return (
    <>
      <Card elevation={5} sx={{ p: 2, mb: 3, width: "100%" }}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Typography variant="h6" align="left">
              Scenario specification
            </Typography>
          </Grid>
          <Grid item xs={6}>
            <Controller
              name="scenarioProperties.scenario_name"
              control={control}
              rules={{
                required: REQUIRED_ERROR_MSG,
              }}
              render={({
                field: { onChange, value },
                fieldState: { error },
              }) => (
                <TextField
                  type="text"
                  value={value}
                  label="Scenario name"
                  onChange={(e) => {
                    onChange(e.target.value);
                  }}
                  error={error !== undefined}
                  helperText={error?.message}
                  variant="standard"
                  style={{ width: "75%" }}
                />
              )}
            />
          </Grid>

          <Grid item xs={6}>
            <Controller
              name="scenarioProperties.num_instances"
              control={control}
              rules={{
                required: REQUIRED_ERROR_MSG,
                min: {
                  value: 1,
                  message: SHOULD_BE_GREATER_0_MSG,
                },
              }}
              render={({
                field: { onChange, value },
                fieldState: { error },
              }) => (
                <TextField
                  type="number"
                  value={value}
                  label="Total number of iterations"
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
                  style={{ width: "75%" }}
                />
              )}
            />
          </Grid>
          <Grid item xs={6}>
            <Controller
              name="scenarioProperties.approach"
              control={control}
              rules={{
                required: REQUIRED_ERROR_MSG,
              }}
              render={({
                field: { onChange, value },
                fieldState: { error },
              }) => (
                <>
                  <InputLabel id="approach-select-label">Approach</InputLabel>
                  <Select
                    required={true}
                    sx={{ minWidth: 250 }}
                    labelId="approach-select-label"
                    id="approach-select"
                    value={value}
                    name={"approach"}
                    label="Approach"
                    onChange={(e) => {
                      onChange(String(e.target.value));
                    }}
                    error={error !== undefined}
                    variant="standard"
                  >
                    <MenuItem value={"CA"}>CA | Calendar Only</MenuItem>
                    <MenuItem value={"AR"}>AR | Add/Remove Only</MenuItem>
                    <MenuItem value={"CO"}>CO | CA/AR combined </MenuItem>
                    <MenuItem value={"CAAR"}>CAAR | First CA then AR </MenuItem>
                    <MenuItem value={"ARCA"}>ARCA | First AR then CA </MenuItem>
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

export default GlobalConstraints;
