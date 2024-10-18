import { createSelector } from "@reduxjs/toolkit";
import { RootState } from "../store";

export const selectSelectedAssets = createSelector(
  (state: RootState) => state.uiState.selectedAssets,
  (state: RootState) => state.assets,
  (selectedAssets, assets) => {
    return assets.filter((asset) => selectedAssets.includes(asset.id));
  }
);

export const selectSelectedConstraintsAsset = createSelector(
  (state: RootState) => state.uiState.selectedAssets,
  (state: RootState) =>
    state.assets.filter((asset) => asset.type === "OPTIMOS_CONSTRAINTS"),
  (selectedAssets, assets) => {
    if (selectedAssets.length === 0) return null;
    return assets.filter((asset) => selectedAssets.includes(asset.id))[0];
  }
);

export const selectSelectedTimetableAsset = createSelector(
  (state: RootState) => state.uiState.selectedAssets,
  (state: RootState) =>
    state.assets.filter((asset) => asset.type === "TIMETABLE"),
  (selectedAssets, assets) => {
    if (selectedAssets.length === 0) return null;

    return assets.filter((asset) => selectedAssets.includes(asset.id))[0];
  }
);

export const selectSelectedBPMNAsset = createSelector(
  (state: RootState) => state.uiState.selectedAssets,
  (state: RootState) => state.assets.filter((asset) => asset.type === "BPMN"),
  (selectedAssets, assets) => {
    if (selectedAssets.length === 0) return null;
    return assets.filter((asset) => selectedAssets.includes(asset.id))[0];
  }
);

export const selectAssets = (state: RootState) => state.assets;

export const selectIsAssetSelected = createSelector(
  (state: RootState) => state.uiState.selectedAssets,
  (_: RootState, assetId: string) => assetId,
  (selectedAssets, assetId) => selectedAssets.includes(assetId)
);
