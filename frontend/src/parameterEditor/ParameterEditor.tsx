import {
  Button,
  Grid,
  Stack,
  Stepper,
  Tooltip,
  Text,
  Box,
  Group,
  Tabs,
  Alert,
} from "@mantine/core";

import { useEffect, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import { useDispatch, useSelector } from "react-redux";

import { TABS, TabNames, getIndexOfTab } from "../hooks/useTabVisibility";
import OptimosConfig from "../constraintEditors/OptimosConfig";
import ResourceConstraints from "../resourceConstraints/ResourceConstraints";
import ScenarioConstraints from "../constraintEditors/ScenarioConstraints";
import { ValidationTab } from "../validation/ValidationTab";
import { MasterFormData, useMasterFormData } from "../hooks/useMasterFormData";
import { constraintResolver } from "../validation/validationFunctions";
import { generateConstraints } from "../generateContraints";
import {
  addAsset,
  AssetType,
  updateByMasterForm,
} from "../redux/slices/assetsSlice";
import {
  addRunningOptimization,
  deselectAsset,
  deselectAssets,
  setCurrentTab,
  setSidePanel,
} from "../redux/slices/uiStateSlice";
import {
  selectSelectedAssets,
  selectSelectedBPMNAsset,
} from "../redux/selectors/assetSelectors";
import React from "react";
import { selectCurrentTab } from "../redux/selectors/uiStateSelectors";
import { createFormContext } from "@mantine/form";
import { MasterFormProvider, useMasterForm } from "../hooks/useFormContext";
import { IconInfoCircle } from "@tabler/icons-react";
import { CustomStepIcon } from "./CustomStepIcon";
import { ProcessingRequest } from "../redux/slices/optimosApi";
import { store } from "../redux/store";
import { showError, showSuccess } from "../util/helpers";
import { showNotification } from "@mantine/notifications";
import { useStartOptimizationStartOptimizationPostMutation } from "../redux/slices/optimosApi";
import { useNavigate } from "react-router-dom";
import { setConfig } from "../redux/slices/optimosConfigSlice";

const tooltip_desc: Record<TABS, string> = {
  [TABS.GLOBAL_CONSTRAINTS]:
    "Define the algorithm, approach and number of iterations",
  [TABS.SCENARIO_CONSTRAINTS]:
    "Define the top-level restrictions like the time granularity and the maximum work units",
  [TABS.RESOURCE_CONSTRAINTS]:
    "Define resource specific constraints, their maximum capacity and working masks",
  [TABS.VALIDATION_RESULTS]: "View the validation results of the constraints",
};

export const ParameterEditor = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const activeTab = useSelector(selectCurrentTab);
  const [
    masterFormData,
    hasSimParamsFile,
    hasConsParamsFile,
    hasBPMNFile,
    simParamsError,
    constraintsError,
    bpmnError,
  ] = useMasterFormData();

  const masterForm = useMasterForm({
    validate: constraintResolver,
    transformValues: (values) => ({
      ...values,
      constraints: {
        ...values.constraints,
        time_var: parseInt(values?.constraints?.time_var as any),
      },
    }),
  });

  useEffect(() => {
    console.log("Resetting form");
    masterForm.setValues(masterFormData);
  }, [masterFormData]);

  const { getTransformedValues, validate } = masterForm;

  const getStepContent = (index: TABS) => {
    switch (index) {
      case TABS.GLOBAL_CONSTRAINTS:
        return <OptimosConfig />;
      case TABS.SCENARIO_CONSTRAINTS:
        return <ScenarioConstraints />;
      case TABS.RESOURCE_CONSTRAINTS:
        return <ResourceConstraints />;
      case TABS.VALIDATION_RESULTS:
        return <ValidationTab />;
      default:
        return null;
    }
  };

  const handleConfigSave = async () => {
    dispatch(updateByMasterForm(getTransformedValues()));
    dispatch(setConfig(getTransformedValues().optimosConfig));

    masterForm.resetTouched();
    masterForm.resetDirty();
  };

  const createConstraintsFromSimParams = async () => {
    if (!hasSimParamsFile) return;
    const simParams = getTransformedValues().simulationParameters;
    if (!simParams) return;
    const constraints = generateConstraints(simParams);
    dispatch(
      addAsset({
        id: uuidv4(),
        name: "generated_constraints.json",
        type: AssetType.OPTIMOS_CONSTRAINTS,
        value: constraints,
      })
    );
  };

  const [startOptimizationQuery, { isLoading }] =
    useStartOptimizationStartOptimizationPostMutation();
  const startOptimization = async () => {
    const processingRequest: ProcessingRequest = {
      config: getTransformedValues().optimosConfig,
      bpmn_model: selectSelectedBPMNAsset(store.getState()).value,
      timetable: getTransformedValues().simulationParameters,
      constraints: getTransformedValues().constraints,
    };

    const { data, error } = await startOptimizationQuery({ processingRequest });
    if (error) {
      showError(
        `Failed to start optimization: ${
          "message" in error ? error?.message : error.toString()
        }`
      );
    } else {
      dispatch(addRunningOptimization(data?.id));
      showSuccess("Optimization started successfully");
    }
    dispatch(deselectAssets());
    dispatch(setSidePanel({ side: "left", open: false }));
    dispatch(setSidePanel({ side: "right", open: true }));
    navigate(`/results/${data?.id}`);
  };

  useEffect(() => {
    if (
      hasBPMNFile &&
      hasSimParamsFile &&
      hasConsParamsFile &&
      !simParamsError &&
      !constraintsError &&
      !bpmnError
    ) {
      console.log("Validating with", validate);
      validate();
    }
  }, [
    hasBPMNFile,
    hasSimParamsFile,
    hasConsParamsFile,
    simParamsError,
    constraintsError,
    bpmnError,
  ]);

  return (
    <Box>
      {(!hasBPMNFile || !hasSimParamsFile) &&
        !constraintsError &&
        !simParamsError && (
          <Alert
            variant="light"
            color="blue"
            title="Info"
            ta="left"
            icon={<IconInfoCircle />}
          >
            Select a Optimos Configuration and Simulation Model from the input
            assets on the left.
          </Alert>
        )}

      {hasSimParamsFile && simParamsError && (
        <Alert
          variant="light"
          color="blue"
          title="Info"
          ta="left"
          icon={<IconInfoCircle />}
        >
          The Simulation Parameters don't follow the required format. Please
          upload a correct version before proceeding. Technical details:
          <pre>{simParamsError.message}</pre>
        </Alert>
      )}

      {!simParamsError && hasConsParamsFile && constraintsError && (
        <Alert
          variant="light"
          color="blue"
          title="Info"
          ta="left"
          icon={<IconInfoCircle />}
        >
          The Constraints don't follow the required format. Please upload a
          correct version before proceeding. Technical details:
          <pre>{constraintsError.message}</pre>
        </Alert>
      )}

      {hasBPMNFile && bpmnError && !simParamsError && (
        <Alert
          variant="light"
          color="blue"
          title="Info"
          ta="left"
          icon={<IconInfoCircle />}
        >
          The BPMN file doesn't match the Simulation Model or the BPMN File is
          invalid. Please make sure the Simulation Model (Timetable) contains
          the necessary tasks and gateways. Technical details:
          <pre>{bpmnError.message}</pre>
        </Alert>
      )}

      {hasBPMNFile &&
        hasSimParamsFile &&
        !simParamsError &&
        !hasConsParamsFile &&
        !bpmnError && (
          <Alert
            variant="light"
            color="blue"
            title="Info"
            ta="left"
            icon={<IconInfoCircle />}
          >
            You have only selected a Simulation Model, please select an Optimos
            Configuration file or click "Generate Constraints" below.
            <br />
            <Button onClick={createConstraintsFromSimParams} mt="md">
              Generate Constraints
            </Button>
          </Alert>
        )}

      {hasBPMNFile &&
        hasSimParamsFile &&
        hasConsParamsFile &&
        !simParamsError &&
        !constraintsError &&
        !bpmnError && (
          <MasterFormProvider form={masterForm}>
            <form
              onSubmit={masterForm.onSubmit(
                async (e, t) => {
                  await handleConfigSave();
                  await startOptimization();
                },
                () => {
                  alert(
                    "There are still errors in the parameters, please correct them before submitting."
                  );
                }
              )}
            >
              <Grid justify="center" w="100%">
                <Grid.Col span={{ sm: 12, md: 10 }}>
                  <Tabs
                    w="100%"
                    value={activeTab}
                    onChange={(tab) =>
                      dispatch(setCurrentTab(tab as unknown as TABS))
                    }
                  >
                    <Tabs.List justify="center">
                      {Object.entries(TabNames).map(([key, label], index) => (
                        <Tooltip
                          key={label}
                          label={tooltip_desc[key]}
                          position="top"
                          withArrow
                        >
                          <Tabs.Tab
                            key={label}
                            value={key}
                            leftSection={
                              <CustomStepIcon
                                currentTab={key as TABS}
                                activeStep={activeTab}
                              />
                            }
                          >
                            {label}
                          </Tabs.Tab>
                        </Tooltip>
                      ))}
                    </Tabs.List>
                    {Object.values(TABS).map((tab) => (
                      <Tabs.Panel key={tab} value={tab}>
                        {getStepContent(tab)}
                      </Tabs.Panel>
                    ))}
                  </Tabs>

                  <Group justify="center" mt="lg">
                    <Button
                      onClick={handleConfigSave}
                      variant="outline"
                      loading={isLoading}
                    >
                      Save Config
                    </Button>
                    <Button type="submit">Start Optimization</Button>
                  </Group>
                </Grid.Col>
              </Grid>
            </form>
          </MasterFormProvider>
        )}
    </Box>
  );
};
