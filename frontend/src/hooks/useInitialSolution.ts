import { useContext, useMemo } from "react";
import { useParams } from "react-router-dom";
import { useReport } from "./useReport";
import { JsonSolution } from "../redux/slices/optimosApi";
import React from "react";

export const InitialSolutionContext = React.createContext<JsonSolution | null>(
  null
);

export const useInitialSolution = (): JsonSolution | null => {
  const initialSolution = useContext(InitialSolutionContext);
  return initialSolution;
};

export const useInitialResource = (resourceId: string) => {
  const solution = useInitialSolution();
  return solution?.resource_info[resourceId];
};
