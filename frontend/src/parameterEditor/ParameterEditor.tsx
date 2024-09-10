import {
  Button,
  Grid,
  Stack,
  Step,
  StepButton,
  Stepper,
  Tooltip,
} from "@mui/material";

import { v4 as uuidv4 } from "uuid";
import { useEffect, useCallback, useContext, useMemo, useState } from "react";

import { TABS, TabNames, getIndexOfTab } from "../hooks/useTabVisibility";
import GlobalConstraints from "../constraintEditors/GlobalConstraints";
import { FormProvider, useForm } from "react-hook-form";
import ResourceConstraints from "../resourceConstraints/ResourceConstraints";
import ScenarioConstraints from "../constraintEditors/ScenarioConstraints";

import { ValidationTab } from "../validation/ValidationTab";
import { MasterFormData, useMasterFormData } from "../hooks/useMasterFormData";
import { CustomStepIcon } from "./CustomStepIcon";
import { constraintResolver } from "../validation/validationFunctions";

import { validateBPMN } from "../validation/validateBPMN";
import React from "react";
import { generateConstraints } from "../generateContraints";
import { useDispatch, useSelector } from "react-redux";
import {
  selectSelectedAssets,
  selectSelectedBPMNAsset,
} from "../redux/selectors/assetSelectors";
import { selectCurrentTab } from "../redux/selectors/uiStateSelectors";
import { addAsset, updateByMasterForm } from "../redux/slices/assetsSlice";
import { setCurrentTab } from "../redux/slices/uiStateSlice";

const tooltip_desc: Record<string, string> = {
  GLOBAL_CONSTRAINTS: "Define the algorithm, approach and number of iterations",
  SCENARIO_CONSTRAINTS:
    "Define the top-level restrictions like the time granularity and the maximum work units",
  RESOURCE_CONSTRAINTS:
    "Define resource specific constraints, their maximum capacity and working masks",
  SIMULATION_RESULTS: "",
};

export const ParamterEditor = () => {
  const dispatch = useDispatch();
  const selectedAssets = useSelector(selectSelectedAssets);

  const activeTab = useSelector(selectCurrentTab);

  const [
    masterFormData,
    hasSimParamsFile,
    hasConsParamsFile,
    hasConfigFile,
    hasBPMNFile,
    simParamsError,
    constraintsError,
    bpmnError,
  ] = useMasterFormData();

  const masterForm = useForm<MasterFormData>({
    values: masterFormData,
    mode: "onChange",
    resolver: constraintResolver,
  });
  const { getValues, trigger } = masterForm;

  useEffect(() => {
    trigger();
  }, [trigger, masterFormData]);

  const getStepContent = (index: TABS) => {
    switch (index) {
      case TABS.GLOBAL_CONSTRAINTS:
        return <GlobalConstraints />;
      case TABS.SCENARIO_CONSTRAINTS:
        return <ScenarioConstraints />;
      case TABS.RESOURCE_CONSTRAINTS:
        return <ResourceConstraints />;
      case TABS.VALIDATION_RESULTS:
        return <ValidationTab />;
    }
  };

  const handleConfigSave = async () => {
    dispatch(updateByMasterForm(getValues()));

    masterForm.reset({}, { keepValues: true });
  };
  const createConstraintsFromSimParams = async () => {
    if (!hasSimParamsFile) return;
    const simParams = getValues().simulationParameters;
    if (!simParams) return;
    const constraints = generateConstraints(simParams);
    dispatch(
      addAsset({
        id: uuidv4(),
        name: "generated_constraints.json",
        type: "OPTIMOS_CONSTRAINTS",
        value: constraints,
      })
    );
  };

  return (
    <div>
      {!(hasBPMNFile || hasSimParamsFile) &&
        !constraintsError &&
        !simParamsError && (
          <p className="my-4 py-2 prose prose-md prose-slate max-w-lg text-center">
            Select a Optimos Configuration and Simulation Model from the input
            assets on the left.
          </p>
        )}

      {hasSimParamsFile && simParamsError && (
        <p className="my-4 py-2 prose prose-md prose-slate max-w-lg text-center">
          The Simulation Parameters doesn't follow the required format. Please
          upload a correct version, before proceeding. Technical details:
          <pre>{simParamsError.message}</pre>
        </p>
      )}

      {!simParamsError && hasConsParamsFile && constraintsError && (
        <p className="my-4 py-2 prose prose-md prose-slate max-w-lg text-center">
          The Constraints doesn't follow the required format. Please upload a
          correct version, before proceeding. Technical details:
          <pre>{constraintsError.message}</pre>
        </p>
      )}

      {hasBPMNFile && bpmnError && !simParamsError && (
        <p className="my-4 py-2 prose prose-md prose-slate max-w-lg text-center">
          The BPMN file doesn't match the Simulation Model or the BPMN File is
          invalid. Please make sure, the Simulation Model (Timetable) contains
          the necessary tasks and gateways. Technical details:
          <pre>{bpmnError.message}</pre>
        </p>
      )}

      {hasBPMNFile &&
        hasSimParamsFile &&
        !simParamsError &&
        !hasConsParamsFile &&
        !bpmnError && (
          <p className="my-4 py-2 prose prose-md prose-slate max-w-lg text-center">
            You have only selected a Simulation Model, please select a Optimos
            Configuration file or click "Generate Constraints" below.
            <Button
              variant="contained"
              color="primary"
              onClick={createConstraintsFromSimParams}
            >
              Generate Constraints
            </Button>
          </p>
        )}

      {hasBPMNFile &&
        hasSimParamsFile &&
        hasConsParamsFile &&
        !simParamsError &&
        !constraintsError &&
        !bpmnError && (
          <FormProvider {...masterForm}>
            <form
              onSubmit={masterForm.handleSubmit(
                async (e, t) => {
                  await handleConfigSave();
                  // TODO: Do something with the form data
                },
                () => {
                  alert(
                    "There are still errors in the parameters, please correct them before submitting."
                  );
                }
              )}
            >
              <Grid container alignItems="center" justifyContent="center">
                <Grid item xs={12} sx={{ paddingTop: "10px" }}>
                  <Grid
                    item
                    container
                    xs={12}
                    alignItems="center"
                    justifyContent="center"
                    sx={{ paddingTop: "20px" }}
                  >
                    <Stepper
                      nonLinear
                      alternativeLabel
                      activeStep={getIndexOfTab(activeTab)}
                      connector={<></>}
                    >
                      {Object.entries(TabNames).map(([key, label]) => {
                        const keyTab = key as keyof typeof TABS;
                        const valueTab: TABS = TABS[keyTab];

                        return (
                          <Step key={label}>
                            <Tooltip title={tooltip_desc[key]}>
                              <StepButton
                                color="inherit"
                                onClick={() => {
                                  dispatch(setCurrentTab(valueTab));
                                }}
                                icon={
                                  <CustomStepIcon
                                    activeStep={activeTab}
                                    currentTab={valueTab}
                                  />
                                }
                              >
                                {label}
                              </StepButton>
                            </Tooltip>
                          </Step>
                        );
                      })}
                    </Stepper>
                    <Grid container mt={3} style={{ marginBottom: "2%" }}>
                      {getStepContent(activeTab)}
                    </Grid>
                  </Grid>
                </Grid>
                <Grid
                  container
                  item
                  xs={12}
                  alignItems="center"
                  justifyContent="center"
                  textAlign={"center"}
                >
                  <Grid item container justifyContent="center">
                    <Stack direction="row" spacing={2}>
                      <Button
                        onClick={handleConfigSave}
                        variant="outlined"
                        color="primary"
                        sx={{ marginTop: "20px" }}
                      >
                        Save Config
                      </Button>
                      <Button
                        type="submit"
                        variant="contained"
                        color="primary"
                        sx={{ marginTop: "20px" }}
                      >
                        Start Optimization
                      </Button>
                    </Stack>
                  </Grid>
                </Grid>
              </Grid>
            </form>
          </FormProvider>
        )}
    </div>
  );
};
