import { combineReducers, configureStore } from "@reduxjs/toolkit";
import { assetReducer } from "./slices/assetsSlice";
import {
  FLUSH,
  PAUSE,
  PERSIST,
  persistReducer,
  persistStore,
  PURGE,
  REGISTER,
  REHYDRATE,
} from "redux-persist";
import storage from "redux-persist/lib/storage";
import { uiStateReducer } from "./slices/uiStateSlice";
import { compressTransform } from "./compressTransform";
import { apiSliceMiddleware, apiSliceReducer } from "./slices/apiSlice";
import { setupListeners } from "@reduxjs/toolkit/query";

const persistConfig = {
  key: "root",
  version: 1,
  storage,
  transform: [compressTransform],
};

const rootReducer = combineReducers({
  assets: assetReducer,
  uiState: uiStateReducer,
  api: apiSliceReducer,
});

const persistedReducer = persistReducer(persistConfig, rootReducer);

export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    //@ts-ignore
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }).concat(apiSliceMiddleware),
});

setupListeners(store.dispatch);
export const persistor = persistStore(store);

export type RootState = ReturnType<typeof store.getState>;

export type AppDispatch = typeof store.dispatch;
