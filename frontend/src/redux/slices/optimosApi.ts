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
export type GetReportFileGetReportIdGetApiResponse =
  /** status 200 Report file retrieved */ any;
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
  num_instances: number;
  algorithm: string;
  approach: string;
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
};
export type DistributionType =
  | "fix"
  | "default"
  | "norm"
  | "expon"
  | "exponnorm"
  | "gamma"
  | "triang"
  | "lognorm";
export type DistributionParameter = {
  value: number | number;
};
export type ArrivalTimeDistribution = {
  distribution_name: DistributionType;
  distribution_params: DistributionParameter[];
};
export type Day =
  | "MONDAY"
  | "TUESDAY"
  | "WEDNESDAY"
  | "THURSDAY"
  | "FRIDAY"
  | "SATURDAY"
  | "SUNDAY";
export type TimePeriod = {
  from_: Day;
  to: Day;
  begin_time: string;
  end_time: string;
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
};
export type EventDistribution = {};
export type BatchType = "Sequential" | "Concurrent" | "Parallel";
export type Distribution = {
  key: string | number;
  value: number;
};
export type RuleType =
  | "ready_wt"
  | "large_wt"
  | "daily_hour"
  | "week_day"
  | "size";
export type Comparator = "<" | "<=" | ">" | ">=" | "=";
export type FiringRule = {
  attribute: RuleType;
  comparison: Comparator;
  value: Day | number;
};
export type BatchingRule = {
  task_id: string;
  type: BatchType;
  size_distrib: Distribution[];
  duration_distrib: Distribution[];
  firing_rules: FiringRule[][];
};
export type TimetableType = {
  resource_profiles: ResourcePool[];
  arrival_time_distribution: ArrivalTimeDistribution;
  arrival_time_calendar: TimePeriod[];
  gateway_branching_probabilities: GatewayBranchingProbability[];
  task_resource_distribution: TaskResourceDistributions[];
  resource_calendars: ResourceCalendar[];
  event_distribution: EventDistribution;
  batch_processing?: BatchingRule[];
  start_time?: string;
  total_cases?: number;
};
export type SizeRuleConstraints = {
  id: string;
  tasks: string[];
  batch_type: BatchType;
  rule_type: RuleType;
  duration_fn: string;
  min_size: number;
  max_size: number;
};
export type ReadyWtRuleConstraints = {
  id: string;
  tasks: string[];
  batch_type: BatchType;
  rule_type: RuleType;
  min_wt: number;
  max_wt: number;
};
export type LargeWtRuleConstraints = {
  id: string;
  tasks: string[];
  batch_type: BatchType;
  rule_type: RuleType;
  min_wt: number;
  max_wt: number;
};
export type WeekDayRuleConstraints = {
  id: string;
  tasks: string[];
  batch_type: BatchType;
  rule_type: RuleType;
  allowed_days: Day[];
};
export type DailyHourRuleConstraints = {
  id: string;
  tasks: string[];
  batch_type: BatchType;
  rule_type: RuleType;
  allowed_hours: number[];
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
export type CancelResponse = {
  message: string;
};
export const {
  useStartOptimizationStartOptimizationPostMutation,
  useGetReportFileGetReportIdGetQuery,
  useCancelOptimizationCancelOptimizationIdPostMutation,
  useGetStatusStatusIdGetQuery,
} = injectedRtkApi;
