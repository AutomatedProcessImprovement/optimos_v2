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
import GlobalConstraints from "../constraintEditors/GlobalConstraints";
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
import { setCurrentTab } from "../redux/slices/uiStateSlice";
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
    transformValues: (values) => ({
      ...values,
      constraints: {
        ...values.constraints,
        time_var: parseInt(values.constraints.time_var as any),
      },
    }),
  });

  const { getTransformedValues, validate } = masterForm;

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
    dispatch(updateByMasterForm(getTransformedValues()));

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
                  // TODO: Do something with the form data
                },
                () => {
                  alert(
                    "There are still errors in the parameters, please correct them before submitting."
                  );
                }
              )}
            >
              <Grid justify="center" w="100%">
                <Grid.Col span={{ sm: 12, md: 10, lg: 8 }}>
                  <Tabs
                    w="100%"
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
