import { useEffect, useState } from "react";

export enum TABS {
  GLOBAL_CONSTRAINTS = "Global Constraints",
  SCENARIO_CONSTRAINTS = "Scenario Constraints",
  RESOURCE_CONSTRAINTS = "Resource Constraints",
  VALIDATION_RESULTS = "Constraint Validation",
}

export const TabNames: Record<TABS, string> = {
  [TABS.GLOBAL_CONSTRAINTS]: "Global Constraints",
  [TABS.SCENARIO_CONSTRAINTS]: "Scenario Constraints",
  [TABS.RESOURCE_CONSTRAINTS]: "Resource Constraints",
  [TABS.VALIDATION_RESULTS]: "Constraint Validation",
};

export const getIndexOfTab = (tab: TABS | string) => {
  return Object.values(TABS).indexOf(tab as any);
};
