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
import createCompressor from "redux-persist-transform-compress";
import { uiStateReducer } from "./slices/uiStateSlice";

const compressor = createCompressor();

const persistConfig = {
  key: "root",
  version: 1,
  storage,
  transform: [compressor],
};

const rootReducer = combineReducers({
  assets: assetReducer,
  uiState: uiStateReducer,
});

const persistedReducer = persistReducer(persistConfig, rootReducer);

export const store = configureStore({
  reducer: persistedReducer,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [FLUSH, REHYDRATE, PAUSE, PERSIST, PURGE, REGISTER],
      },
    }),
});

export const persistor = persistStore(store);

export type RootState = ReturnType<typeof store.getState>;

export type AppDispatch = typeof store.dispatch;
