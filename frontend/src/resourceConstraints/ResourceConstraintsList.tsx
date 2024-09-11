import { Card, Grid, NumberInput, Text, Checkbox, Group } from "@mantine/core";

import type { FC } from "react";
import { useState, useEffect, useMemo } from "react";

import {
  REQUIRED_ERROR_MSG,
  SHOULD_BE_GREATER_0_MSG,
} from "../validationMessages";
import { ConstraintMaskInput } from "./ConstraintMaskInput";

import type { MasterFormData } from "../hooks/useMasterFormData";
import React from "react";
import { useMasterFormContext } from "../hooks/useFormContext";

type ResourceConstraintsListProps = {
  currResourceId: string;
};
export const ResourceConstraintsList: FC<ResourceConstraintsListProps> = (
  props
) => {
  const { currResourceId } = props;
  const form = useMasterFormContext();
  const resources = form.values?.constraints?.resources;
  const index = useMemo(
    () => resources.findIndex((resource) => resource.id === currResourceId),
    [resources, currResourceId]
  );

  return (
    <Grid gutter="md">
      <Grid.Col span={12}>
        <Card shadow="sm" padding="lg" style={{ width: "100%" }}>
          <Grid>
            <Grid.Col span={12}>
              <Text fw={500} size="lg" ta="left">
                {currResourceId}'s constraints
              </Text>
            </Grid.Col>

            <Grid.Col span={6}>
              <NumberInput
                label="Max weekly shifts"
                min={1}
                step={1}
                error={
                  form.errors?.constraints?.resources?.[index]?.constraints
                    ?.global_constraints?.max_weekly_cap?.message
                }
                {...form.getInputProps(
                  `constraints.resources.${index}.constraints.global_constraints.max_weekly_cap`
                )}
                style={{ width: "50%" }}
              />
            </Grid.Col>

            <Grid.Col span={6}>
              <NumberInput
                label="Max daily capacity"
                min={1}
                step={1}
                error={
                  form.errors?.constraints?.resources?.[index]?.constraints
                    ?.global_constraints?.max_daily_cap?.message
                }
                {...form.getInputProps(
                  `constraints.resources.${index}.constraints.global_constraints.max_daily_cap`
                )}
                style={{ width: "50%" }}
              />
            </Grid.Col>

            <Grid.Col span={6}>
              <NumberInput
                label="Max consecutive capacity"
                min={1}
                step={1}
                error={
                  form.errors?.constraints?.resources?.[index]?.constraints
                    ?.global_constraints?.max_consecutive_cap?.message
                }
                {...form.getInputProps(
                  `constraints.resources.${index}.constraints.global_constraints.max_consecutive_cap`
                )}
                style={{ width: "50%" }}
              />
            </Grid.Col>

            <Grid.Col span={6}>
              <NumberInput
                label="Max shifts per day"
                min={1}
                step={1}
                error={
                  form.errors?.constraints?.resources?.[index]?.constraints
                    ?.global_constraints?.max_shifts_day?.message
                }
                {...form.getInputProps(
                  `constraints.resources.${index}.constraints.global_constraints.max_shifts_day`
                )}
                style={{ width: "50%" }}
              />
            </Grid.Col>

            <Grid.Col span={6}>
              <NumberInput
                label="Max shifts per week"
                min={1}
                step={1}
                error={
                  form.errors?.constraints?.resources?.[index]?.constraints
                    ?.global_constraints?.max_shifts_week?.message
                }
                {...form.getInputProps(
                  `constraints.resources.${index}.constraints.global_constraints.max_shifts_week`
                )}
                style={{ width: "50%" }}
              />
            </Grid.Col>

            <Grid.Col span={6}>
              <Group>
                <Checkbox
                  label="Human resource?"
                  checked={
                    form.getInputProps(
                      `constraints.resources.${index}.constraints.global_constraints.is_human`
                    ).value
                  }
                  {...form.getInputProps(
                    `constraints.resources.${index}.constraints.global_constraints.is_human`
                  )}
                />
              </Group>
            </Grid.Col>
          </Grid>
        </Card>
      </Grid.Col>

      <Grid.Col span={12}>
        <ConstraintMaskInput resourceId={currResourceId} />
      </Grid.Col>
    </Grid>
  );
};
