import React from "react";
import { Provider, useDispatch, useSelector } from "react-redux";
import { PersistGate } from "redux-persist/integration/react";
import { persistor, store } from "./redux/store";
import { ParameterEditor } from "./parameterEditor/ParameterEditor";
import "@mantine/core/styles.css";
import "@mantine/dropzone/styles.css";
import "@mantine/notifications/styles.css";
import { Notifications } from "@mantine/notifications";

import { HomePage } from "./pages/HomePage";
import {
  AppShell,
  Box,
  Burger,
  createTheme,
  MantineProvider,
  Text,
} from "@mantine/core";

import { createBrowserRouter, Outlet, RouterProvider } from "react-router-dom";
import { router } from "./router";
import { AssetsView } from "./components/AssetsView";
import { OutputView } from "./components/OutputView";
import {
  selectLeftPanelOpen,
  selectRightPanelOpen,
} from "./redux/selectors/uiStateSelectors";
import { toggleSidePanel } from "./redux/slices/uiStateSlice";

export function App() {
  const theme = createTheme({
    /** Put your mantine theme override here */
  });

  return (
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}>
        <MantineProvider theme={theme}>
          <Notifications />
          <RouterProvider router={router}></RouterProvider>
        </MantineProvider>
      </PersistGate>
    </Provider>
  );
}
