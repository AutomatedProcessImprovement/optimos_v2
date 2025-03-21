import { createSlice, PayloadAction } from "@reduxjs/toolkit";
import {
  AgentType,
  ConfigType,
  LegacyApproachAbbreviation,
  Mode,
} from "./optimosApi";
import { PURGE } from "redux-persist";
import { updateByMasterForm } from "./assetsSlice";

const initialState: ConfigType = {
  scenario_name: "My first scenario",
  num_cases: 100,
  approach: LegacyApproachAbbreviation.Ba,
  max_non_improving_actions: 1000,
  max_iterations: 1000,
  max_actions_per_iteration: null,
  agent: AgentType.SimulatedAnnealing,
  mode: Mode.Batching,
  max_solutions: null,
  iterations_per_solution: null,
  max_number_of_variations_per_action: null,
  sa_solution_order: "random",
  sa_temperature: null,
  sa_cooling_rate: null,
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
