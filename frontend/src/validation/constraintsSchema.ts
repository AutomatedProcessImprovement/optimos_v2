import * as yup from "yup";

export const constraintsSchema = yup.object().shape({
  time_var: yup.number().required(),
  max_cap: yup.number().required(),
  max_shift_size: yup.number().required(),
  max_shift_blocks: yup.number().required(),
  hours_in_day: yup.number().required(),
  resources: yup
    .array()
    .of(
      yup.object().shape({
        id: yup.string().required(),
        constraints: yup.object().shape({
          global_constraints: yup.object().shape({
            max_weekly_cap: yup.number().required(),
            max_daily_cap: yup.number().required(),
            max_consecutive_cap: yup.number().required(),
            max_shifts_day: yup.number().required(),
            max_shifts_week: yup.number().required(),
            is_human: yup.boolean().required(),
          }),
          daily_start_times: yup.object().shape({
            monday: yup.string().nullable(),
            tuesday: yup.string().nullable(),
            wednesday: yup.string().nullable(),
            thursday: yup.string().nullable(),
            friday: yup.string().nullable(),
            saturday: yup.string().nullable(),
            sunday: yup.string().nullable(),
          }),
          never_work_masks: yup.object().shape({
            monday: yup.number().required(),
            tuesday: yup.number().required(),
            wednesday: yup.number().required(),
            thursday: yup.number().required(),
            friday: yup.number().required(),
            saturday: yup.number().required(),
            sunday: yup.number().required(),
          }),
          always_work_masks: yup.object().shape({
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
    .required(),
});
