import { createSelector } from "@reduxjs/toolkit";

export const selectCurrentTab = createSelector(
  (state) => state.uiState.currentTab,
  (currentTab) => currentTab
);
