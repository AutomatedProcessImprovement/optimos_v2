import { createSelector } from "@reduxjs/toolkit";
import { RootState } from "../store";

export const selectCurrentTab = (state: RootState) => state.uiState.currentTab;
export const selectRunningOptimizations = (state: RootState) =>
  state.uiState.runningOptimizations;
