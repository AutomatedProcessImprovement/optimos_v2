import { createSlice, PayloadAction } from "@reduxjs/toolkit";

import {
  ConsParams,
  Constraints,
  ScenarioProperties,
  SimParams,
} from "../../types/optimos_json_type";
import { PURGE } from "redux-persist";
import { MasterFormData } from "../../hooks/useMasterFormData";

export type AssetType = {
  id: string;
  name: string;
  parsing_error?: string;
} & (
  | {
      type: "BPMN";
      value?: string;
    }
  | {
      type: "OPTIMOS_CONFIG";
      value?: ScenarioProperties;
    }
  | {
      type: "OPTIMOS_CONSTRAINTS";
      value?: ConsParams;
    }
  | {
      type: "TIMETABLE";
      value?: SimParams;
    }
);

const initialState = [] as AssetType[];

export const assetSlice = createSlice({
  name: "assets",
  initialState,
  reducers: {
    addAsset: (state, action: PayloadAction<AssetType>) => {
      state.push(action.payload);
    },
    removeAsset: (state, action: PayloadAction<string>) => {
      state = state.filter((asset) => asset.id !== action.payload);
    },
    updateAsset: (
      state,
      action: PayloadAction<{ id: string; value: AssetType }>
    ) => {
      const { id, value } = action.payload;
      const index = state.findIndex((asset) => asset.id === id);
      if (index !== -1) {
        state[index] = value;
      }
    },
    updateByMasterForm: (state, action: PayloadAction<MasterFormData>) => {
      const { constraints, simulationParameters, scenarioProperties } =
        action.payload;
      const constraintsAsset = state.find(
        (asset) => asset.type === "OPTIMOS_CONSTRAINTS"
      );
      const simParamsAsset = state.find((asset) => asset.type === "TIMETABLE");
      const configFileAsset = state.find(
        (asset) => asset.type === "OPTIMOS_CONFIG"
      );
      if (constraintsAsset) {
        constraintsAsset.value = constraints;
      }
      if (simParamsAsset) {
        simParamsAsset.value = simulationParameters;
      }
      if (configFileAsset) {
        configFileAsset.value = scenarioProperties;
      }
    },
  },
  extraReducers: (builder) => {
    builder.addCase(PURGE, (state) => {
      state = [];
    });
  },
});

export const { addAsset, removeAsset, updateAsset } = assetSlice.actions;

export const assetReducer = assetSlice.reducer;
