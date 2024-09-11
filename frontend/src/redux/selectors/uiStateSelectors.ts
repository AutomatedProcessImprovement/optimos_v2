import { createSelector } from "@reduxjs/toolkit";

export const selectCurrentTab = (state) => state.uiState.currentTab;
