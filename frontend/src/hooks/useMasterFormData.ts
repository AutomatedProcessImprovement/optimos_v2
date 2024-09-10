import useJsonFile from "./useJsonFile";
import { useYAMLFile } from "./useYAMLFile";
import { useFileFromAsset } from "./useFetchedAsset";

import { useEffect, useMemo, useState } from "react";
import { timetableSchema } from "../validation/timetableSchema";
import { constraintsSchema } from "../validation/constraintsSchema";
import { validateBPMN } from "../validation/validateBPMN";
import { useSelector } from "react-redux";
import {
  selectSelectedBPMNAsset,
  selectSelectedConfigAsset,
  selectSelectedConstraintsAsset,
  selectSelectedTimetableAsset,
} from "../redux/selectors/assetSelectors";
import {
  ConsParams,
  SimParams,
  ScenarioProperties,
} from "../types/optimos_json_type";

export type MasterFormData = {
  constraints?: ConsParams;
  simulationParameters?: SimParams;
  scenarioProperties: ScenarioProperties;
};

const DEFAULT_CONFIG: ScenarioProperties = {
  scenario_name: "My first scenario",
  num_instances: 100,
  algorithm: "HC-FLEX",
  approach: "CAAR",
};

export const useMasterFormData = () => {
  const constraintsAsset = useSelector(selectSelectedConstraintsAsset);
  const simParamsAsset = useSelector(selectSelectedTimetableAsset);
  const configFileAsset = useSelector(selectSelectedConfigAsset);
  const bpmnAsset = useSelector(selectSelectedBPMNAsset);

  const masterFormData = useMemo<MasterFormData>(
    () => ({
      constraints: constraintsAsset?.value,
      simulationParameters: simParamsAsset?.value,
      scenarioProperties: configFileAsset?.value || DEFAULT_CONFIG,
    }),
    [constraintsAsset, simParamsAsset, configFileAsset]
  );

  const hasSimParamsFile = simParamsAsset !== null;
  const hasConsParamsFile = constraintsAsset !== null;
  const hasConfigFile = configFileAsset !== null;
  const hasBPMNFile = bpmnAsset !== null;

  const simParamsError = useMemo<Error | null>(() => {
    if (simParamsAsset?.parsing_error) {
      return new Error(
        `Simulation parameters file is not a valid JSON file: ${simParamsAsset?.parsing_error}`
      );
    }
    try {
      if (simParamsAsset?.value) {
        timetableSchema.validateSync(simParamsAsset?.value);
      }
    } catch (e) {
      return e as Error;
    }
    return null;
  }, [simParamsAsset]);

  const constraintsError = useMemo<Error | null>(() => {
    if (constraintsAsset?.parsing_error) {
      return new Error(
        `Constraints file is not a valid JSON file: ${constraintsAsset?.parsing_error}`
      );
    }
    try {
      if (constraintsAsset?.value) {
        constraintsSchema.validateSync(constraintsAsset?.value);
      }
    } catch (e) {
      return e as Error;
    }
    return null;
  }, [constraintsAsset]);

  const [bpmnError, setBpmnError] = useState<Error | null>(null);
  useEffect(() => {
    if (bpmnAsset && hasSimParamsFile) {
      const simParams = simParamsAsset?.value;
      if (!simParams || !bpmnAsset.value) return;

      validateBPMN(bpmnAsset.value, simParams)
        .then(() => {
          setBpmnError(null);
        })
        .catch((e) => {
          setBpmnError(e);
        });
    }
  }, [bpmnAsset, hasSimParamsFile, simParamsAsset]);

  return [
    masterFormData,
    hasSimParamsFile,
    hasConsParamsFile,
    hasConfigFile,
    hasBPMNFile,
    simParamsError,
    constraintsError,
    bpmnError,
  ] as const;
};
