import { useLocation, useSearchParams } from "@remix-run/react";
import { TABS, getIndexOfTab } from "./useTabVisibility";
import { useEffect } from "react";

export const useOptimosTab = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const tabIndex = parseInt(searchParams.get("tabIndex") || "0");

  useEffect(() => {
    if (searchParams.get("tabIndex") === null) {
      setSearchParams({ tabIndex: "0" });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const setTab = (index: number) => {
    setSearchParams({ tabIndex: index.toString() });
  };
  return [tabIndex, setTab] as const;
};
