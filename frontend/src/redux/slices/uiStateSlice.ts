import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { PURGE } from "redux-persist";
import { TABS } from "../../hooks/useTabVisibility";
import { removeAsset } from "./assetsSlice";

const uiStateSlice = createSlice({
  name: "uiState",
  initialState: {
    currentTab: TABS.SCENARIO_CONSTRAINTS,
    selectedAssets: [] as string[],
    runningOptimizations: [] as string[],
    sidePanelsOpen: {
      left: true,
      right: true,
    },
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
    deselectAssets: (state) => {
      state.selectedAssets = [];
    },
    addRunningOptimization: (state, action: PayloadAction<string>) => {
      state.runningOptimizations.splice(0, 0, action.payload);
    },
    removeRunningOptimization: (state, action: PayloadAction<string>) => {
      state.runningOptimizations = state.runningOptimizations.filter(
        (id) => id !== action.payload
      );
    },
    toggleSidePanel: (state, action: PayloadAction<"left" | "right">) => {
      state.sidePanelsOpen[action.payload] =
        !state.sidePanelsOpen[action.payload];
    },
    setSidePanel: (
      state,
      action: PayloadAction<{ side: "left" | "right"; open: boolean }>
    ) => {
      state.sidePanelsOpen[action.payload.side] = action.payload.open;
    },
  },
  extraReducers: (builder) => {
    builder.addCase(PURGE, (state) => {
      state = {
        currentTab: TABS.SCENARIO_CONSTRAINTS,
        selectedAssets: [],
        runningOptimizations: [],
        sidePanelsOpen: {
          left: true,
          right: true,
        },
      };
    });
    builder.addCase(removeAsset, (state, action) => {
      state.selectedAssets = state.selectedAssets.filter(
        (asset) => asset !== action.payload
      );
    });
  },
});

export const {
  setCurrentTab,
  selectAsset,
  deselectAsset,
  addRunningOptimization,
  removeRunningOptimization,
  toggleSidePanel,
  setSidePanel,
  deselectAssets,
} = uiStateSlice.actions;

export const uiStateReducer = uiStateSlice.reducer;
