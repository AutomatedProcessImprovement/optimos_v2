import { apiSlice as api } from "./apiSlice";
const injectedRtkApi = api.injectEndpoints({
  endpoints: (build) => ({
    startOptimizationStartOptimizationPost: build.mutation<
      StartOptimizationStartOptimizationPostApiResponse,
      StartOptimizationStartOptimizationPostApiArg
    >({
      query: (queryArg) => ({
        url: `/start_optimization`,
        method: "POST",
        body: queryArg.processingRequest,
      }),
    }),
    getReportZipFileGetReportZipIdGet: build.query<
      GetReportZipFileGetReportZipIdGetApiResponse,
      GetReportZipFileGetReportZipIdGetApiArg
    >({
      query: (queryArg) => ({ url: `/get_report_zip/${queryArg.id}` }),
    }),
    getReportFileGetReportIdGet: build.query<
      GetReportFileGetReportIdGetApiResponse,
      GetReportFileGetReportIdGetApiArg
    >({
      query: (queryArg) => ({ url: `/get_report/${queryArg.id}` }),
    }),
    cancelOptimizationCancelOptimizationIdPost: build.mutation<
      CancelOptimizationCancelOptimizationIdPostApiResponse,
      CancelOptimizationCancelOptimizationIdPostApiArg
    >({
      query: (queryArg) => ({
        url: `/cancel_optimization/${queryArg.id}`,
        method: "POST",
      }),
    }),
    getStatusStatusIdGet: build.query<
      GetStatusStatusIdGetApiResponse,
      GetStatusStatusIdGetApiArg
    >({
      query: (queryArg) => ({ url: `/status/${queryArg.id}` }),
    }),
  }),
  overrideExisting: false,
});
export { injectedRtkApi as optimosApi };
export type StartOptimizationStartOptimizationPostApiResponse =
  /** status 202 Successful Response */ OptimizationResponse;
export type StartOptimizationStartOptimizationPostApiArg = {
  processingRequest: ProcessingRequest;
};
export type GetReportZipFileGetReportZipIdGetApiResponse =
  /** status 200 Report zip file retrieved */ any;
export type GetReportZipFileGetReportZipIdGetApiArg = {
  /** The identifier of the zip file */
  id: string;
};
export type GetReportFileGetReportIdGetApiResponse =
  /** status 200 Report zip file retrieved */ JsonReport;
export type GetReportFileGetReportIdGetApiArg = {
  /** The identifier of the zip file */
  id: string;
};
export type CancelOptimizationCancelOptimizationIdPostApiResponse =
  /** status 202 Successful Response */ CancelResponse;
export type CancelOptimizationCancelOptimizationIdPostApiArg = {
  id: string;
};
export type GetStatusStatusIdGetApiResponse =
  /** status 200 Successful Response */ string;
export type GetStatusStatusIdGetApiArg = {
  id: string;
};
export type OptimizationResponse = {
  message: string;
  json_url: string;
  id: string;
};
export type ValidationError = {
  loc: (string | number)[];
  msg: string;
  type: string;
};
export type HttpValidationError = {
  detail?: ValidationError[];
};
export type ConfigType = {
  scenario_name: string;
  num_cases: number;
  max_non_improving_actions: number;
  max_iterations: number;
  max_solutions: number | null;
  iterations_per_solution: number | null;
  max_actions_per_iteration: number | null;
  max_number_of_variations_per_action: number | null;
  approach: string;
  agent: AgentType;
  mode: Mode;
};
export type Resource = {
  id: string;
  name: string;
  cost_per_hour: number;
  amount: number;
  calendar: string;
  assigned_tasks: string[];
};
export type ResourcePool = {
  id: string;
  name: string;
  resource_list: Resource[];
  fixed_cost_fn?: string;
};
export type DistributionParameter = {
  value: number | number;
};
export type ArrivalTimeDistribution = {
  distribution_name: DISTRIBUTION_TYPE;
  distribution_params: DistributionParameter[];
};
export type TimePeriod = {
  from_: DAY;
  to: DAY;
  begin_time: string;
  end_time: string;
  probability?: number | null;
};
export type Probability = {
  path_id: string;
  value: number;
};
export type GatewayBranchingProbability = {
  gateway_id: string;
  probabilities: Probability[];
};
export type TaskResourceDistribution = {
  resource_id: string;
  distribution_name: string;
  distribution_params: DistributionParameter[];
};
export type TaskResourceDistributions = {
  task_id: string;
  resources: TaskResourceDistribution[];
};
export type ResourceCalendar = {
  id: string;
  name: string;
  time_periods: TimePeriod[];
  workload_ratio?: TimePeriod[] | null;
};
export type Distribution = {
  key: string | number;
  value: number;
};
export type FiringRule = {
  attribute: RULE_TYPE;
  comparison: COMPARATOR;
  value: DAY | number;
};
export type BatchingRule = {
  task_id: string;
  type: BATCH_TYPE;
  size_distrib: Distribution[];
  duration_distrib: Distribution[];
  firing_rules: FiringRule[][];
};
export type ParallelTaskProbability = {
  parallel_tasks: number;
  probability: number;
};
export type TimePeriodWithParallelTaskProbability = {
  from_: DAY;
  to: DAY;
  begin_time: string;
  end_time: string;
  multitask_info?: ParallelTaskProbability[] | null;
};
export type MultitaskResourceInfo = {
  resource_id: string;
  r_workload: number;
  multitask_info?: ParallelTaskProbability[] | null;
  weekly_probability?: TimePeriodWithParallelTaskProbability[][] | null;
};
export type Multitask = {
  type: string;
  values: MultitaskResourceInfo[];
};
export type GranuleSize = {
  value?: number;
  time_unit?: "MINUTES";
};
export type TimetableType = {
  resource_profiles: ResourcePool[];
  arrival_time_distribution: ArrivalTimeDistribution;
  arrival_time_calendar: TimePeriod[];
  gateway_branching_probabilities: GatewayBranchingProbability[];
  task_resource_distribution: TaskResourceDistributions[];
  resource_calendars: ResourceCalendar[];
  batch_processing?: BatchingRule[];
  start_time?: string;
  total_cases?: number;
  multitask?: Multitask | null;
  model_type?: ("FUZZY" | "CRISP") | null;
  granule_size?: GranuleSize | null;
  event_distribution?: object[] | null;
  global_attributes?: object[] | null;
  case_attributes?: object[] | null;
  event_attributes?: object[] | null;
  branch_rules?: object[] | null;
};
export type SizeRuleConstraints = {
  id: string;
  tasks: string[];
  batch_type: BATCH_TYPE;
  rule_type: RULE_TYPE;
  duration_fn: string;
  cost_fn: string;
  min_size: number | null;
  max_size: number | null;
};
export type ReadyWtRuleConstraints = {
  id: string;
  tasks: string[];
  batch_type: BATCH_TYPE;
  rule_type: RULE_TYPE;
  min_wt: number;
  max_wt: number;
};
export type LargeWtRuleConstraints = {
  id: string;
  tasks: string[];
  batch_type: BATCH_TYPE;
  rule_type: RULE_TYPE;
  min_wt: number | null;
  max_wt: number | null;
};
export type WeekDayRuleConstraints = {
  id: string;
  tasks: string[];
  batch_type: BATCH_TYPE;
  rule_type: RULE_TYPE;
  allowed_days: DAY[];
};
export type DailyHourRuleConstraints = {
  id: string;
  tasks: string[];
  batch_type: BATCH_TYPE;
  rule_type: RULE_TYPE;
  allowed_hours: {
    [key: string]: number[];
  };
};
export type GlobalConstraints = {
  max_weekly_cap: number;
  max_daily_cap: number;
  max_consecutive_cap: number;
  max_shifts_day: number;
  max_shifts_week: number;
  is_human: boolean;
};
export type WorkMasks = {
  monday?: number | null;
  tuesday?: number | null;
  wednesday?: number | null;
  thursday?: number | null;
  friday?: number | null;
  saturday?: number | null;
  sunday?: number | null;
};
export type ResourceConstraints = {
  global_constraints: GlobalConstraints;
  never_work_masks: WorkMasks;
  always_work_masks: WorkMasks;
};
export type ConstraintsResourcesItem = {
  id: string;
  constraints: ResourceConstraints;
};
export type ConstraintsType = {
  batching_constraints?: (
    | SizeRuleConstraints
    | ReadyWtRuleConstraints
    | LargeWtRuleConstraints
    | WeekDayRuleConstraints
    | DailyHourRuleConstraints
  )[];
  resources?: ConstraintsResourcesItem[];
  max_cap?: number;
  max_shift_size?: number;
  max_shift_blocks?: number;
  hours_in_day?: number;
  time_var?: number;
};
export type ProcessingRequest = {
  config: ConfigType;
  bpmn_model: string;
  timetable: TimetableType;
  constraints: ConstraintsType;
};
export type JsonGlobalInfo = {
  average_cost: number;
  average_time: number;
  average_resource_utilization: number;
  total_cost: number;
  total_time: number;
  average_batching_waiting_time: number;
  average_waiting_time: number;
};
export type JsonResourceModifiers = {
  deleted: boolean | null;
  added: boolean | null;
  shifts_modified: boolean | null;
  tasks_modified: boolean | null;
};
export type JsonResourceInfo = {
  id: string;
  name: string;
  worked_time: number;
  available_time: number;
  utilization: number;
  cost_per_week: number;
  total_cost: number;
  hourly_rate: number;
  is_human: boolean;
  max_weekly_capacity: number;
  max_daily_capacity: number;
  max_consecutive_capacity: number;
  timetable_bitmask: WorkMasks;
  original_timetable_bitmask: WorkMasks;
  work_hours_per_week: number;
  never_work_bitmask: WorkMasks;
  always_work_bitmask: WorkMasks;
  assigned_tasks: string[];
  added_tasks: string[];
  removed_tasks: string[];
  total_batching_waiting_time: number;
  modifiers: JsonResourceModifiers;
};
export type JsonAction = {
  type: string;
  params: any;
};
export type JsonSolution = {
  is_base_solution: boolean;
  solution_no: number;
  global_info: JsonGlobalInfo;
  resource_info: {
    [key: string]: JsonResourceInfo;
  };
  deleted_resources_info: {
    [key: string]: JsonResourceInfo;
  };
  timetable: TimetableType;
  actions: JsonAction[];
};
export type JsonParetoFront = {
  solutions: JsonSolution[];
};
export type JsonReport = {
  name: string;
  created_at: string;
  constraints: ConstraintsType;
  bpmn_definition: string;
  base_solution: JsonSolution;
  pareto_fronts: JsonParetoFront[];
  is_final: boolean;
  approach?: string | null;
};
export type CancelResponse = {
  message: string;
};
export enum AgentType {
  TabuSearch = "tabu_search",
  SimulatedAnnealing = "simulated_annealing",
  ProximalPolicyOptimization = "proximal_policy_optimization",
  TabuSearchRandom = "tabu_search_random",
  SimulatedAnnealingRandom = "simulated_annealing_random",
  ProximalPolicyOptimizationRandom = "proximal_policy_optimization_random",
}
export enum Mode {
  Batching = "batching",
  Calendar = "calendar",
}
export enum DISTRIBUTION_TYPE {
  Fix = "fix",
  Uniform = "uniform",
  Norm = "norm",
  Expon = "expon",
  Exponnorm = "exponnorm",
  Gamma = "gamma",
  Triang = "triang",
  Lognorm = "lognorm",
}
export enum DAY {
  Monday = "MONDAY",
  Tuesday = "TUESDAY",
  Wednesday = "WEDNESDAY",
  Thursday = "THURSDAY",
  Friday = "FRIDAY",
  Saturday = "SATURDAY",
  Sunday = "SUNDAY",
}
export enum BATCH_TYPE {
  Sequential = "Sequential",
  Concurrent = "Concurrent",
  Parallel = "Parallel",
}
export enum RULE_TYPE {
  ReadyWt = "ready_wt",
  LargeWt = "large_wt",
  DailyHour = "daily_hour",
  WeekDay = "week_day",
  Size = "size",
}
export enum COMPARATOR {
  "<",
  "<=",
  ">",
  ">=",
  "=",
}
export const {
  useStartOptimizationStartOptimizationPostMutation,
  useGetReportZipFileGetReportZipIdGetQuery,
  useGetReportFileGetReportIdGetQuery,
  useCancelOptimizationCancelOptimizationIdPostMutation,
  useGetStatusStatusIdGetQuery,
} = injectedRtkApi;
