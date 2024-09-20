import { useMemo } from "react";
import { useParams } from "react-router-dom";
import { useReport } from "./useReport";

export const useInitialSolution = () => {
  const [report] = useReport();
  return report.baseSolution;
};

export const useInitialResource = (resourceId: string) => {
  const solution = useInitialSolution();
  return solution.resourceInfo[resourceId];
};
