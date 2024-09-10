import React from "react";
import { Provider } from "react-redux";
import { PersistGate } from "redux-persist/integration/react";
import { persistor, store } from "./redux/store";
import { ParamterEditor } from "./parameterEditor/ParameterEditor";

export function App() {
  return (
    <Provider store={store}>
      <PersistGate loading={null} persistor={persistor}></PersistGate>
      <ParamterEditor></ParamterEditor>
    </Provider>
  );
}
