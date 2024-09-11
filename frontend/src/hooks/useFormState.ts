import { useEffect, useMemo } from "react";
import * as yup from "yup";
import {
  MIN_LENGTH_REQUIRED_MSG,
  REQUIRED_ERROR_MSG,
  SHOULD_BE_NUMBER_MSG,
} from "../validationMessages";
import { yupResolver } from "@hookform/resolvers/yup";
import type { ConsParams } from "~/shared/optimos_json_type";
import { useMasterForm } from "./useFormContext";

const useFormState = (consJsonData?: ConsParams) => {
  const constraintsValidationSchema = useMemo(
    () =>
      yup.object({
        time_var: yup.number(),
        max_cap: yup.number(),
        max_shift_size: yup.number(),
        max_shift_blocks: yup.number(),
        hours_in_day: yup.number(),
        resource_constraints: yup
          .array()
          .of(
            yup.object({
              id: yup.string().required(),
              constraints: yup.object({
                global_constraints: yup.object({
                  max_weekly_cap: yup
                    .number()
                    .required(REQUIRED_ERROR_MSG)
                    .typeError(SHOULD_BE_NUMBER_MSG),
                  max_daily_cap: yup
                    .number()
                    .required(REQUIRED_ERROR_MSG)
                    .typeError(SHOULD_BE_NUMBER_MSG),
                  max_consecutive_cap: yup
                    .number()
                    .required(REQUIRED_ERROR_MSG)
                    .typeError(SHOULD_BE_NUMBER_MSG),
                  max_shifts_day: yup
                    .number()
                    .required(REQUIRED_ERROR_MSG)
                    .typeError(SHOULD_BE_NUMBER_MSG),
                  max_shifts_week: yup
                    .number()
                    .required(REQUIRED_ERROR_MSG)
                    .typeError(SHOULD_BE_NUMBER_MSG),
                  is_human: yup
                    .boolean()
                    .required(REQUIRED_ERROR_MSG)
                    .typeError(SHOULD_BE_NUMBER_MSG),
                }),
                daily_start_times: yup.object({
                  monday: yup.number().nullable().default(null),
                  tuesday: yup.number().nullable().default(null),
                  wednesday: yup.number().nullable().default(null),
                  thursday: yup.number().nullable().default(null),
                  friday: yup.number().nullable().default(null),
                  saturday: yup.number().nullable().default(null),
                  sunday: yup.number().nullable().default(null),
                }),
                never_work_masks: yup.object({
                  monday: yup.number().required(),
                  tuesday: yup.number().required(),
                  wednesday: yup.number().required(),
                  thursday: yup.number().required(),
                  friday: yup.number().required(),
                  saturday: yup.number().required(),
                  sunday: yup.number().required(),
                }),
                always_work_masks: yup.object({
                  monday: yup.number().required(),
                  tuesday: yup.number().required(),
                  wednesday: yup.number().required(),
                  thursday: yup.number().required(),
                  friday: yup.number().required(),
                  saturday: yup.number().required(),
                  sunday: yup.number().required(),
                }),
              }),
            })
          )
          .min(1, MIN_LENGTH_REQUIRED_MSG("resource_constraints")),
      }),
    []
  );

  const formState = useMasterForm<ConsParams>({
    resolver: yupResolver(constraintsValidationSchema) as any,
    mode: "onBlur",
  });

  const { reset } = formState;

  useEffect(() => {
    if (consJsonData !== undefined) {
      reset(consJsonData);
    }
  }, [consJsonData, reset]);

  return { formState };
};

export default useFormState;
