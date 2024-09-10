/*
Config
*/

export interface ScenarioProperties {
  scenario_name: string;
  num_instances: number;
  algorithm: "HC-FLEX" | "HC-STRICT" | "TS" | "ALL";
  approach: "CA" | "AR" | "CO" | "CAAR" | "ARCA" | "ALL";
}

/*
 * Constraints & Simulation Parameters
 */

export interface ConstraintWorkMask {
  monday: number;
  tuesday: number;
  wednesday: number;
  thursday: number;
  friday: number;
  saturday: number;
  sunday: number;
}
export type Shift = ConstraintWorkMask & {
  total?: number;
  resource_id?: string;
};

export interface DailyStartTimes {
  monday: string | null;
  tuesday: string | null;
  wednesday: string | null;
  thursday: string | null;
  friday: string | null;
  saturday: string | null;
  sunday: string | null;
}

export interface SimParams {
  resource_profiles: ResourceProfile[];
  arrival_time_distribution: ArrivalTimeDistribution;
  arrival_time_calendar: TimePeriod[];
  gateway_branching_probabilities: GatewayBranchingProbability[];
  task_resource_distribution: TaskResourceDistribution[];
  event_distribution: EventDistribution;
  resource_calendars: ResourceCalendar[];
}

export interface ResourceProfile {
  id: string;
  name: string;
  resource_list: ResourceListItem[];
}

export interface ResourceListItem {
  id: string;
  name: string;
  cost_per_hour: number;
  amount: number;
  calendar: string;
  assigned_tasks: string[];
}

export interface ArrivalTimeDistribution {
  distribution_name: string;
  distribution_params: DistributionParam[];
}

export interface DistributionParam {
  value: number;
}

export interface GatewayBranchingProbability {
  gateway_id: string;
  probabilities: Probability[];
}

export interface Probability {
  path_id: string;
  value: number;
}

export interface TaskResourceDistribution {
  task_id: string;
  resources: Resource[];
}

export interface Resource {
  resource_id: string;
  distribution_name: string;
  distribution_params: DistributionParam2[];
}

export interface DistributionParam2 {
  value: number;
}

export interface EventDistribution {}

export interface ResourceCalendar {
  id: string;
  name: string;
  time_periods: TimePeriod[];
}

export interface TimePeriod {
  from: string;
  to: string;
  beginTime: string;
  endTime: string;
}

export interface ConsParams {
  time_var: number;
  max_cap: number;
  max_shift_size: number;
  max_shift_blocks: number;
  hours_in_day: number;
  resources: ResourceConstraints[];
}

export interface ResourceConstraints {
  id: string;
  constraints: Constraints;
}

export interface Constraints {
  global_constraints: GlobalConstraints;
  daily_start_times: DailyStartTimes;
  never_work_masks: ConstraintWorkMask;
  always_work_masks: ConstraintWorkMask;
}

export interface GlobalConstraints {
  max_weekly_cap: number;
  max_daily_cap: number;
  max_consecutive_cap: number;
  max_shifts_day: number;
  max_shifts_week: number;
  is_human: boolean;
}

/*
Result Types 
*/

export interface JSONReport {
  name: string;
  approach: string;

  constraints: ConsParams;
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
  timetableBitmask: ConstraintWorkMask;
  originalTimetableBitmask: ConstraintWorkMask;
  workHoursPerWeek: number;
  neverWorkBitmask: ConstraintWorkMask;
  alwaysWorkBitmask: ConstraintWorkMask;

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
  timetable: SimParams;
  actions: BaseAction[];
}
