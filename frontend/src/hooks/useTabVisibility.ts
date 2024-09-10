import { useEffect, useState } from "react";

export enum TABS {
  GLOBAL_CONSTRAINTS,
  SCENARIO_CONSTRAINTS,
  RESOURCE_CONSTRAINTS,
  VALIDATION_RESULTS,
}

export const TabNames: Record<string, string> = {
  GLOBAL_CONSTRAINTS: "Global Constraints",
  SCENARIO_CONSTRAINTS: "Scenario Constraints",
  RESOURCE_CONSTRAINTS: "Resource Constraints",
  VALIDATION_RESULTS: "Constraint Validation",
};

export const getIndexOfTab = (tab: TABS) => {
  return Object.keys(TabNames).indexOf(tab.toString());
};
