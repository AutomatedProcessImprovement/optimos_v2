import * as yup from "yup";
import {
  distributionParametersLength,
  DistributionType,
  isStrArrUnique,
  testProbabilitiesSum,
  testUniqueAttributes,
  testUniqueKeys,
} from "../types/prosimos_scheme";
import { COMPARATOR } from "../redux/slices/optimosApi";

const distributionSchema = {
  distribution_name: yup.string().required(),
  distribution_params: yup
    .array()
    .when("distribution_name", (distributionName: string | string[], _) => {
      const dtype = (
        Array.isArray(distributionName) ? distributionName[0] : distributionName
      ) as DistributionType;
      if (!Object.keys(DistributionType).includes(dtype)) {
        return yup
          .mixed()
          .test("type", "Invalid distribution type", () => false);
      }

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

export const timetableSchema = yup.object({
  model_type: yup.string(),
  process_model: yup.string(),
  granule_size: yup.object({
    time_unit: yup.string(),
    value: yup.number().positive().integer(),
  }),
  // total_cases and start_time have a soft requirement, they must be present when submitting data,
  // but can be omitted when loading data from custom parameters files
  total_cases: yup.number().positive().integer(),
  start_time: yup.string(),
  arrival_time_distribution: yup.object().required().shape(distributionSchema),
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
  event_distribution: yup.object().required(),
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
                comparison: yup.mixed().oneOf(Object.values(COMPARATOR)),
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
            return yup
              .mixed()
              .test("type", "Invalid case attribute type", () => false);
        }
      }),
    })
  ),
});
