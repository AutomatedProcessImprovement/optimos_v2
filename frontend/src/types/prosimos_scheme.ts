import * as yup from "yup";
import { formatDate } from "../util/helpers";

const distributionSchema = {
  distribution_name: yup.string().required(),
  distribution_params: yup
    .mixed()
    .when("distribution_name", (distributionName: string | string[], _) => {
      const dtype = distributionName as DistributionType;
      return yup
        .array()
        .of(
          yup.object().shape({
            value: yup.number().required(),
          })
        )
        .required()
        .min(
          distributionParametersLength(dtype),
          `Missed required parameters for ${distributionName}`
        );
    }),
};

const calendarPeriod = yup.object({
  from: yup.string().required(),
  to: yup.string().required(),
  beginTime: yup.string().required(),
  endTime: yup.string().required(),
});

export const prosimosConfigurationSchema = yup.object({
  model_type: yup.string().default("CRISP"),
  process_model: yup.string(),
  granule_size: yup.object({
    time_unit: yup.string().default("MINUTES"),
    value: yup.number().positive().integer().default(30),
  }),
  // total_cases and start_time have a soft requirement, they must be present when submitting data,
  // but can be omitted when loading data from custom parameters files
  total_cases: yup.number().positive().integer(),
  start_time: yup.string().default(formatDate(new Date())),
  arrival_time_distribution: yup.object().shape(distributionSchema),
  arrival_time_calendar: yup
    .array()
    .of(calendarPeriod)
    .required()
    .min(1, "At least one arrival calendar is required"),
  resource_calendars: yup
    .array()
    .of(
      yup.object({
        id: yup.string().required(),
        name: yup.string().required(),
        time_periods: yup.array().of(calendarPeriod).required(),
      })
    )
    .required(),
  resource_profiles: yup
    .array()
    .of(
      yup.object({
        id: yup.string().required(),
        name: yup.string().required(),
        resource_list: yup
          .array()
          .of(
            yup.object({
              id: yup.string().required(),
              name: yup.string().required(),
              cost_per_hour: yup.number().required(),
              amount: yup.number().positive().integer().required(),
              calendar: yup.string().required(),
              assigned_tasks: yup.array(),
            })
          )
          .min(1, "At least one resource is required")
          .test(
            "unique",
            "Resource profiles must have unique names",
            (resourceList) => {
              const namesArr = resourceList?.map(({ name }) => name ?? "");
              return isStrArrUnique(namesArr);
            }
          )
          .test(
            "unique",
            "Resource profiles must have unique ids",
            (resourceList) => {
              const idsArr = resourceList?.map(({ id }) => id ?? "");
              return isStrArrUnique(idsArr);
            }
          ),
      })
    )
    .required()
    .min(1, "At least one resource profile is required"),
  task_resource_distribution: yup
    .array()
    .of(
      yup.object({
        task_id: yup.string().required(),
        resources: yup
          .array()
          .of(
            yup.object({
              resource_id: yup.string().required(),
              ...distributionSchema,
            })
          )
          .required()
          .min(
            1,
            "At least one resource profile in the resource allocation is required"
          ),
      })
    )
    .required()
    .min(1, "At least one resource allocation is required"),
  gateway_branching_probabilities: yup
    .array()
    .of(
      yup.object({
        gateway_id: yup.string().required(),
        probabilities: yup
          .array()
          .of(
            yup.object({
              path_id: yup.string().required(),
              value: yup.number().max(1).required(),
            })
          )
          .test(
            "sum",
            "Gateway branching probabilities must sum to 1",
            testProbabilitiesSum
          )
          .required(),
      })
    )
    .required(),
  event_distribution: yup.array().of(
    yup.object({
      event_id: yup.string().required(),
      ...distributionSchema,
    })
  ),
  batch_processing: yup.array().of(
    yup.object({
      task_id: yup.string().required(),
      type: yup.string().required(),
      size_distrib: yup
        .array()
        .of(
          yup.object({
            key: yup.string().required(),
            value: yup.number().required(),
          })
        )
        .min(1)
        .test(
          "sum",
          "Batching probabilities of the size distribution array must sum to 1",
          testProbabilitiesSum
        )
        .test(
          "unique",
          "Size distributions must have unique keys",
          testUniqueKeys
        ),
      duration_distrib: yup
        .array()
        .of(
          yup.object({
            key: yup.string().required(),
            value: yup.number().required(),
          })
        )
        .min(1)
        .test(
          "unique",
          "Duration distributions must have unique keys",
          testUniqueKeys
        ),
      firing_rules: yup
        .array()
        .of(
          yup
            .array()
            .of(
              yup.object({
                attribute: yup.string().required(),
                comparison: yup.string().required(),
                // string for weekday and numeric string for all others
                value: yup.lazy((value) => {
                  const stringOrNumber = yup.string().when("attribute", {
                    is: (val: string) => val === "week_day",
                    // string is the only limitation (it can contain everything)
                    then: (schema) => schema,
                    // string can contain only digit numbers
                    otherwise: (schema) => schema.matches(/^\d+$/),
                  });
                  const oneValueSchema = stringOrNumber.required();
                  return Array.isArray(value)
                    ? yup.array().of(oneValueSchema)
                    : oneValueSchema;
                }),
              })
            )
            .min(1)
            .test(
              "unique",
              "Firing rules must have unique attributes",
              testUniqueAttributes
            )
        )
        .min(1),
    })
  ),
  case_attributes: yup.array().of(
    yup.object({
      name: yup
        .string()
        .trim()
        .matches(
          /^[a-zA-Z0-9-_,.`':]+$/g,
          "Invalid name. Allowed characters include [a-z], [A-Z], [0-9], and [_,.-:`']"
        )
        .required(),
      type: yup.string().required(),
      values: yup.mixed().when("type", (type: string | string[], _) => {
        switch (type) {
          case "continuous":
            return yup.object().shape(distributionSchema);
          case "discrete":
            return yup
              .array()
              .of(
                yup.object({
                  key: yup.string().required(),
                  value: yup.number().required(),
                })
              )
              .min(1)
              .test(
                "sum",
                "Case attributes values probabilities must sum to 1",
                testProbabilitiesSum
              );
          default:
            throw new Error(`Invalid case attribute type: ${type}`);
        }
      }),
    })
  ),
  prioritization_rules: yup.array().of(
    yup.object({
      priority_level: yup.number().required().min(1),
      rules: yup
        .array()
        .of(
          yup
            .array()
            .of(
              yup.object({
                attribute: yup.string().required(),
                comparison: yup.string().required(),
                value: yup
                  .mixed<
                    | yup.InferType<typeof prioritizationStringSchema>
                    | yup.InferType<typeof prioritizationNumbersSchema>
                  >()
                  .test("shape", "Invalid values", (value) => {
                    prioritizationStringSchema.isValidSync(value) ||
                      prioritizationNumbersSchema.isValidSync(value);
                  }),
              })
            )
            .min(1)
            .test(
              "unique",
              "Prioritization rules must have unique attributes",
              testUniqueAttributes
            )
        )
        .min(1),
    })
  ),
});

const prioritizationStringSchema = yup.string().required();
const prioritizationNumbersSchema = yup
  .array()
  .of(yup.number())
  .required()
  .min(2, "At least two parameters are required");

type Monday = "MONDAY" | "Monday" | "monday";
type Tuesday = "TUESDAY" | "Tuesday" | "tuesday";
type Wednesday = "WEDNESDAY" | "Wednesday" | "wednesday";
type Thursday = "THURSDAY" | "Thursday" | "thursday";
type Friday = "FRIDAY" | "Friday" | "friday";
type Saturday = "SATURDAY" | "Saturday" | "saturday";
type Sunday = "SUNDAY" | "Sunday" | "sunday";

export type WeekDay =
  | Monday
  | Tuesday
  | Wednesday
  | Thursday
  | Friday
  | Saturday
  | Sunday;

export const weekDays = [
  "MONDAY",
  "TUESDAY",
  "WEDNESDAY",
  "THURSDAY",
  "FRIDAY",
  "SATURDAY",
  "SUNDAY",
] as WeekDay[];

export function testProbabilitiesSum(value: any) {
  if (!value) {
    return true;
  }
  const sum = value.reduce(
    (acc: number, curr: { value: number }) => acc + curr.value,
    0
  );
  return sum === 1;
}

export function testUniqueKeys(items: { key: string }[] | undefined) {
  if (!items) return true;
  const keysArr = items?.map(({ key }) => key ?? "");
  return isStrArrUnique(keysArr);
}

export function testUniqueAttributes(
  items: { attribute: string }[] | undefined
) {
  if (!items) return true;
  const keysArr = items?.map(({ attribute }) => attribute ?? "");
  return isStrArrUnique(keysArr);
}

export const isStrArrUnique = (values: string[] | undefined): boolean => {
  const arrLength = values?.length;
  if (!arrLength || arrLength === 0) return true;
  const set = new Set(values);
  return arrLength === set.size;
};

export enum DistributionType {
  expon = "expon",
  fix = "fix",
  gamma = "gamma",
  lognorm = "lognorm",
  norm = "norm",
  uniform = "uniform",
  default = "default",
  exponnorm = "exponnorm",
  triang = "triang",
}

export const distributionParameters = {
  [DistributionType.expon]: ["Mean (s)", "Min (s)", "Max (s)"],
  [DistributionType.uniform]: ["Min (s)", "Max (s)"],
  [DistributionType.fix]: ["Mean (s)"],
  [DistributionType.gamma]: ["Mean (s)", "Variance (s)", "Min (s)", "Max (s)"],
  [DistributionType.lognorm]: [
    "Mean (s)",
    "Variance (s)",
    "Min (s)",
    "Max (s)",
  ],
  [DistributionType.norm]: ["Mean (s)", "Std Dev (s)", "Min (s)", "Max (s)"],
  [DistributionType.default]: ["Min (s)", "Max (s)"],
  [DistributionType.exponnorm]: [
    "Mean (s)",
    "Variance (s)",
    "Min (s)",
    "Max (s)",
  ],
  [DistributionType.triang]: ["Mean (s)", "Min (s)", "Max (s)"],
};

export const distributionParametersLength = (distr_func: DistributionType) => {
  return distributionParameters[distr_func].length;
};

export type ProsimosConfiguration = yup.InferType<
  typeof prosimosConfigurationSchema
>;

export const prosimosConfigurationDefaultValues: ProsimosConfiguration = {
  model_type: "CRISP",
  granule_size: {
    time_unit: "MINUTES",
    value: 30,
  },
  total_cases: 100,
  start_time: formatDate(new Date()),
  arrival_time_distribution: {
    distribution_name: "expon",
    distribution_params: [
      {
        value: 1,
      },
      {
        value: 0,
      },
      {
        value: 100,
      },
    ],
  },
  arrival_time_calendar: [
    {
      from: "MONDAY",
      to: "FRIDAY",
      beginTime: "09:00:00",
      endTime: "17:00:00",
    },
  ],
  resource_calendars: [
    {
      id: "resource_calendar_1",
      name: "resource_calendar_1",
      time_periods: [
        {
          from: "MONDAY",
          to: "FRIDAY",
          beginTime: "09:00:00",
          endTime: "17:00:00",
        },
      ],
    },
  ],
  resource_profiles: [],
  task_resource_distribution: [],
  gateway_branching_probabilities: [],
  batch_processing: [],
  case_attributes: [],
  prioritization_rules: [],
};
