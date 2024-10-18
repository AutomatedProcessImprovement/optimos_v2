import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import { AgentType, ConfigType } from "./optimosApi";
import { PURGE } from "redux-persist";
import { updateByMasterForm } from "./assetsSlice";

const initialState: ConfigType = {
  scenario_name: "My first scenario",
  num_cases: 100,
  approach: "CAAR",
  max_non_improving_actions: 1000,
  max_iterations: 1000,
  max_actions_per_iteration: null,
  agent: AgentType.TabuSearch,
  disable_batch_optimization: true,
};

export const optimosConfigSlice = createSlice({
  name: "config",
  initialState,
  reducers: {
    setConfigByKey: <T extends keyof ConfigType>(
      state,
      action: PayloadAction<{
        key: T;
        value: ConfigType[T];
      }>
    ) => {
      state[action.payload.key] = action.payload.value;
    },
    setConfig: (state, action: PayloadAction<Partial<ConfigType>>) => {
      return { ...state, ...action.payload };
    },
  },
  extraReducers(builder) {
    builder.addCase(PURGE, (_) => {
      return initialState;
    });
    builder.addCase(updateByMasterForm, (state, action) => {
      return action.payload.optimosConfig;
    });
  },
});

export const { setConfigByKey, setConfig } = optimosConfigSlice.actions;
export const optimosConfigReducer = optimosConfigSlice.reducer;
