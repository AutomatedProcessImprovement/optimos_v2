import { useParams } from "react-router-dom";

import { useEffect, useState } from "react";
import JSZip from "jszip";
import {
  useGetReportFileGetReportIdGetQuery,
  useGetStatusStatusIdGetQuery,
} from "../redux/slices/optimosApi";

export const useReport = () => {
  let { optimizationId } = useParams();

  const [jsonError, setJsonError] = useState<string | null>(null);
  const [reportFilePollingInterval, setReportFilePollingInterval] =
    useState(3000);

  const {
    data: status,
    isLoading: isStatusLoading,
    error: statusError,
  } = useGetStatusStatusIdGetQuery(
    { id: optimizationId },
    { pollingInterval: reportFilePollingInterval, skipPollingIfUnfocused: true }
  );

  const {
    data: report,
    isLoading: isZipLoading,
    error: zipError,
  } = useGetReportFileGetReportIdGetQuery(
    {
      id: optimizationId,
    },
    {
      pollingInterval: reportFilePollingInterval,
      skipPollingIfUnfocused: true,
    }
  );
  useEffect(() => {
    if (status === "completed" || status === "cancelled") {
      setReportFilePollingInterval(0);
    }
  }, [status]);

  return [
    report,
    isStatusLoading || isZipLoading,
    statusError || zipError || jsonError,
  ] as const;
};
