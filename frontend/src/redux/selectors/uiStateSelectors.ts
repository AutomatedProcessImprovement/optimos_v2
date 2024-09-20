import { createSelector } from "@reduxjs/toolkit";
import { RootState } from "../store";

export const selectCurrentTab = (state: RootState) => state.uiState.currentTab;
export const selectRunningOptimizations = (state: RootState) =>
  state.uiState.runningOptimizations;

export const selectRightPanelOpen = (state: RootState) =>
  state.uiState.sidePanelsOpen.right;

export const selectLeftPanelOpen = (state: RootState) =>
  state.uiState.sidePanelsOpen.left;
