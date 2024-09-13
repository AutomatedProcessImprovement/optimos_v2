import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { PURGE } from "redux-persist";
import { TABS } from "../../hooks/useTabVisibility";

const uiStateSlice = createSlice({
  name: "uiState",
  initialState: {
    currentTab: TABS.SCENARIO_CONSTRAINTS,
    selectedAssets: [] as string[],
    runningOptimizations: [] as string[],
  },
  reducers: {
    setCurrentTab: (state, action: PayloadAction<TABS>) => {
      state.currentTab = action.payload;
    },
    selectAsset: (state, action: PayloadAction<string>) => {
      state.selectedAssets = Array.from(
        new Set([...state.selectedAssets, action.payload])
      );
    },
    deselectAsset: (state, action: PayloadAction<string>) => {
      state.selectedAssets = state.selectedAssets.filter(
        (asset) => asset !== action.payload
      );
    },
    addRunningOptimization: (state, action: PayloadAction<string>) => {
      state.runningOptimizations.splice(0, 0, action.payload);
    },
    removeRunningOptimization: (state, action: PayloadAction<string>) => {
      state.runningOptimizations = state.runningOptimizations.filter(
        (id) => id !== action.payload
      );
    },
  },
  extraReducers: (builder) => {
    builder.addCase(PURGE, (state) => {
      state = {
        currentTab: TABS.SCENARIO_CONSTRAINTS,
        selectedAssets: [],
        runningOptimizations: [],
      };
    });
  },
});

export const {
  setCurrentTab,
  selectAsset,
  deselectAsset,
  addRunningOptimization,
  removeRunningOptimization,
} = uiStateSlice.actions;

export const uiStateReducer = uiStateSlice.reducer;
