import { useParams } from "react-router-dom";

import { useEffect, useState } from "react";
import JSZip from "jszip";
import {
  JsonReport,
  optimosApi,
  useGetReportFileGetReportIdGetQuery,
  useGetStatusStatusIdGetQuery,
} from "../redux/slices/optimosApi";
import { store } from "../redux/store";

export const useReport = (): [JsonReport | null, any | null] => {
  let { optimizationId } = useParams();

  const [jsonError, setJsonError] = useState<string | null>(null);
  const [reportFilePollingInterval, setReportFilePollingInterval] =
    useState(3000);

  const [report, setReport] = useState<JsonReport | null>(null);

  const { created_at: lastReportDate } = useGetReportFileGetReportIdGetQuery(
    {
      id: optimizationId,
    },
    {
      pollingInterval: reportFilePollingInterval,
      skipPollingIfUnfocused: true,
      selectFromResult: ({ data, error }) => ({
        created_at: data?.created_at,
        error,
      }),
    }
  );
  useEffect(() => {
    if (status === "completed" || status === "cancelled") {
      setReportFilePollingInterval(0);
    }
  }, [status]);

  useEffect(() => {
    if (!lastReportDate) return;
    if (lastReportDate && lastReportDate <= report?.created_at) return;
    const selector = optimosApi.endpoints.getReportFileGetReportIdGet.select({
      id: optimizationId,
    });
    const { data, isLoading, error } = selector({ api: store.getState().api });

    if (error || (!error && jsonError)) {
      setJsonError(error ? String(error) : null);
    }

    if (isLoading || !data) return;

    if (!report || data.created_at > report?.created_at) {
      setReport(data);
    }
  }, [lastReportDate]);

  return [report, jsonError];
};
