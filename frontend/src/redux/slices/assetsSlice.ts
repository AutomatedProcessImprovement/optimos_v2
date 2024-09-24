import { createSlice, PayloadAction } from "@reduxjs/toolkit";

import { PURGE } from "redux-persist";
import { MasterFormData } from "../../hooks/useMasterFormData";
import { ConfigType, ConstraintsType, TimetableType } from "./optimosApi";

export enum AssetType {
  BPMN = "BPMN",
  OPTIMOS_CONFIG = "OPTIMOS_CONFIG",
  OPTIMOS_CONSTRAINTS = "OPTIMOS_CONSTRAINTS",
  TIMETABLE = "TIMETABLE",
}

export type Asset = {
  id: string;
  name: string;
  parsing_error?: string;
} & (
  | {
      type: AssetType.BPMN;
      value?: string;
    }
  | {
      type: AssetType.OPTIMOS_CONFIG;
      value?: ConfigType;
    }
  | {
      type: AssetType.OPTIMOS_CONSTRAINTS;
      value?: ConstraintsType;
    }
  | {
      type: AssetType.TIMETABLE;
      value?: TimetableType;
    }
);

const initialState = [] as Asset[];

export const assetSlice = createSlice({
  name: "assets",
  initialState,
  reducers: {
    addAsset: (state, action: PayloadAction<Asset>) => {
      state.push(action.payload);
    },
    addAssets: (state, action: PayloadAction<Asset[]>) => {
      state.push(...action.payload);
    },
    removeAsset: (state, action: PayloadAction<string>) => {
      return state.filter((asset) => asset.id !== action.payload);
    },
    updateAsset: (
      state,
      action: PayloadAction<{ id: string; value: Asset }>
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

export const {
  addAsset,
  removeAsset,
  updateAsset,
  updateByMasterForm,
  addAssets,
} = assetSlice.actions;

export const assetReducer = assetSlice.reducer;
