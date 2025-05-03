import { useReport } from "./useReport";

export const useTaskNames = () => {
  const [report] = useReport();
  return report?.task_names ?? {};
};
