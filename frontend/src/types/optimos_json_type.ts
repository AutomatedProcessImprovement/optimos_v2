/*
Result Types 
*/

import {
  ConstraintsType,
  TimetableType,
  WorkMasks,
} from "../redux/slices/optimosApi";

export interface JSONReport {
  name: string;
  approach: string;

  constraints: ConstraintsType;
  bpmnDefinition: string;
  baseSolution: JSONSolution;
  paretoFronts: JSONParetoFront[];

  isFinal: boolean;
}

export interface JSONParetoFront {
  solutions: JSONSolution[];
}

export interface JSONResourceModifiers {
  deleted?: boolean;
  added?: boolean;
  shiftsModified?: boolean;
  tasksModified?: boolean;
}

export interface JSONResourceInfo {
  id: string;
  name: string;

  workedTime: number;
  availableTime: number;
  utilization: number;
  costPerWeek: number;
  totalCost: number;
  hourlyRate: number;
  isHuman: boolean;
  maxWeeklyCapacity: number;
  maxDailyCapacity: number;
  maxConsecutiveCapacity: number;
  timetableBitmask: WorkMasks;
  originalTimetableBitmask: WorkMasks;
  workHoursPerWeek: number;
  neverWorkBitmask: WorkMasks;
  alwaysWorkBitmask: WorkMasks;

  assignedTasks: string[];
  addedTasks: string[];
  removedTasks: string[];

  totalBatchingWaitingTime: number;

  modifiers: JSONResourceModifiers;
}

export interface JSONGlobalInfo {
  averageCost: number;
  averageTime: number;
  averageResourceUtilization: number;
  totalCost: number;
  totalTime: number;
  averageBatchingWaitingTime: number;
  averageWaitingTime: number;
}

export interface BaseAction {
  type: string;
  params: Record<string, any>;
}

export interface JSONSolution {
  isBaseSolution: boolean;
  solutionNo: number;
  globalInfo: JSONGlobalInfo;
  resourceInfo: Record<string, JSONResourceInfo>;
  deletedResourcesInfo: JSONResourceInfo[];
  timetable: TimetableType;
  actions: BaseAction[];
}
