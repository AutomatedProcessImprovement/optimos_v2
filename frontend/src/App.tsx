import React from "react";
import { Provider } from "react-redux";
import { PersistGate } from "redux-persist/integration/react";
import { persistor, store } from "./redux/store";
import { ParameterEditor } from "./parameterEditor/ParameterEditor";
import "@mantine/core/styles.css";
import { MainView } from "./MainView";
import { createTheme, MantineProvider } from "@mantine/core";

export function App() {
  const theme = createTheme({
    /** Put your mantine theme override here */
  });
  return (
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}></PersistGate>
      <MantineProvider theme={theme}>
        <MainView />
      </MantineProvider>
    </Provider>
  );
}
