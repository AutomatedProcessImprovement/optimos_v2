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
} from "@mantine/core";

import { useEffect, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import { useDispatch, useSelector } from "react-redux";

import { TABS, TabNames, getIndexOfTab } from "../hooks/useTabVisibility";
import GlobalConstraints from "../constraintEditors/GlobalConstraints";
import ResourceConstraints from "../resourceConstraints/ResourceConstraints";
import ScenarioConstraints from "../constraintEditors/ScenarioConstraints";
import { ValidationTab } from "../validation/ValidationTab";
import { MasterFormData, useMasterFormData } from "../hooks/useMasterFormData";
import { constraintResolver } from "../validation/validationFunctions";
import { generateConstraints } from "../generateContraints";
import { addAsset, updateByMasterForm } from "../redux/slices/assetsSlice";
import { setCurrentTab } from "../redux/slices/uiStateSlice";
import {
  selectSelectedAssets,
  selectSelectedBPMNAsset,
} from "../redux/selectors/assetSelectors";
import React from "react";
import { selectCurrentTab } from "../redux/selectors/uiStateSelectors";
import { createFormContext } from "@mantine/form";
import { MasterFormProvider, useMasterForm } from "../hooks/useFormContext";

const tooltip_desc: Record<string, string> = {
  GLOBAL_CONSTRAINTS: "Define the algorithm, approach and number of iterations",
  SCENARIO_CONSTRAINTS:
    "Define the top-level restrictions like the time granularity and the maximum work units",
  RESOURCE_CONSTRAINTS:
    "Define resource specific constraints, their maximum capacity and working masks",
  VALIDATION_RESULTS: "View the validation results of the constraints",
};

export const ParameterEditor = () => {
  const dispatch = useDispatch();
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

  const masterForm = useMasterForm({
    initialValues: masterFormData,
    validate: constraintResolver,
  });

  const { getValues, validate } = masterForm;

  useEffect(() => {
    validate();
  }, [validate, masterFormData]);

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
      default:
        return null;
    }
  };

  const handleConfigSave = async () => {
    dispatch(updateByMasterForm(getValues()));

    masterForm.resetTouched();
    masterForm.resetDirty();
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
    <Box>
      {!(hasBPMNFile || hasSimParamsFile) &&
        !constraintsError &&
        !simParamsError && (
          <Text ta="center" c="dimmed" size="sm">
            Select a Optimos Configuration and Simulation Model from the input
            assets on the left.
          </Text>
        )}

      {hasSimParamsFile && simParamsError && (
        <Text ta="center" c="dimmed" size="sm">
          The Simulation Parameters don't follow the required format. Please
          upload a correct version before proceeding. Technical details:
          <pre>{simParamsError.message}</pre>
        </Text>
      )}

      {!simParamsError && hasConsParamsFile && constraintsError && (
        <Text ta="center" c="dimmed" size="sm">
          The Constraints don't follow the required format. Please upload a
          correct version before proceeding. Technical details:
          <pre>{constraintsError.message}</pre>
        </Text>
      )}

      {hasBPMNFile && bpmnError && !simParamsError && (
        <Text ta="center" c="dimmed" size="sm">
          The BPMN file doesn't match the Simulation Model or the BPMN File is
          invalid. Please make sure the Simulation Model (Timetable) contains
          the necessary tasks and gateways. Technical details:
          <pre>{bpmnError.message}</pre>
        </Text>
      )}

      {hasBPMNFile &&
        hasSimParamsFile &&
        !simParamsError &&
        !hasConsParamsFile &&
        !bpmnError && (
          <Text ta="center" c="dimmed" size="sm">
            You have only selected a Simulation Model, please select an Optimos
            Configuration file or click "Generate Constraints" below.
            <Button onClick={createConstraintsFromSimParams} mt="md">
              Generate Constraints
            </Button>
          </Text>
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
                  // TODO: Do something with the form data
                },
                () => {
                  alert(
                    "There are still errors in the parameters, please correct them before submitting."
                  );
                }
              )}
            >
              <Grid justify="center">
                <Grid.Col span={12}>
                  <Grid justify="center">
                    <Tabs
                      value={activeTab}
                      onChange={(tab) =>
                        dispatch(setCurrentTab(tab as unknown as TABS))
                      }
                    >
                      <Tabs.List>
                        {Object.entries(TabNames).map(([key, label], index) => (
                          <Tooltip
                            key={label}
                            label={tooltip_desc[key]}
                            position="top"
                            withArrow
                          >
                            <Tabs.Tab key={label} value={key}>
                              {label}
                            </Tabs.Tab>
                          </Tooltip>
                        ))}
                      </Tabs.List>
                      {Object.entries(TabNames).map(([key, label], index) => (
                        <Tabs.Panel key={label} value={key}>
                          {getStepContent(
                            getIndexOfTab(key as unknown as TABS)
                          )}
                        </Tabs.Panel>
                      ))}
                    </Tabs>
                  </Grid>

                  <Group justify="center" mt="lg">
                    <Button onClick={handleConfigSave} variant="outline">
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
