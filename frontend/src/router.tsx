import { createBrowserRouter } from "react-router-dom";
import { HomePage } from "./pages/HomePage";
import React from "react";
import ResultPage from "./pages/results/ResultPage";
import { Root } from "./Root";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Root,
    children: [
      {
        path: "/",
        Component: HomePage,
      },
      {
        path: "/results/:optimizationId",
        Component: ResultPage,
      },
    ],
  },
]);
