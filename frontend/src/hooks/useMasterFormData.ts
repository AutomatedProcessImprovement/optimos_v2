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
  ConfigType,
  ConstraintsType,
  TimetableType,
} from "../redux/slices/optimosApi";

export type MasterFormData = {
  constraints?: ConstraintsType;
  simulationParameters?: TimetableType;
  scenarioProperties: ConfigType;
};

const DEFAULT_CONFIG: ConfigType = {
  scenario_name: "My first scenario",
  num_instances: 100,
  algorithm: "HC-FLEX",
  approach: "CAAR",
};

export const useMasterFormData = () => {
  const constraintsAsset = useSelector(selectSelectedConstraintsAsset);
  const simParamsAsset = useSelector(selectSelectedTimetableAsset);
  const bpmnAsset = useSelector(selectSelectedBPMNAsset);

  const masterFormData = useMemo<MasterFormData>(
    () => ({
      constraints: constraintsAsset?.value,
      simulationParameters: simParamsAsset?.value,
      scenarioProperties: DEFAULT_CONFIG,
    }),
    [constraintsAsset?.value, simParamsAsset?.value]
  );

  const hasSimParamsFile = !!simParamsAsset;
  const hasConsParamsFile = !!constraintsAsset;
  const hasBPMNFile = !!bpmnAsset;

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

    hasBPMNFile,
    simParamsError,
    constraintsError,
    bpmnError,
  ] as const;
};
