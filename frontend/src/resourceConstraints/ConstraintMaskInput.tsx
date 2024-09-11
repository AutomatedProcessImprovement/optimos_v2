import { FC } from "react";
import { Card, Grid, Text, Button, Group } from "@mantine/core";

import { ConstraintCalendar } from "./ConstraintCalendar";
import { BLANK_CONSTRAINTS, DAYS } from "../helpers";
import { useMasterFormContext } from "../hooks/useFormContext";
import { useDebouncedCallback } from "@mantine/hooks";
import React from "react";

interface Props {
  resourceId: string;
}

export const ConstraintMaskInput: FC<Props> = ({ resourceId }) => {
  const form = useMasterFormContext(); // Using Mantine's form context
  const debouncedTrigger = useDebouncedCallback(form.validate, 300);

  const createOnSelectChange =
    (column: "never_work_masks" | "always_work_masks") =>
    (selection: Array<HTMLElement | SVGElement>) => {
      const constraintsEntries = selection.map((element) => {
        const index = parseInt(element.dataset.index!);
        const day = element.dataset.day as (typeof DAYS)[number];
        return { index, day };
      });

      // Group by column, then day
      const newConstraints = constraintsEntries.reduce(
        (acc, { index, day }) => ({
          ...acc,
          [day]: acc[day] | (1 << (23 - index)),
        }),
        { ...BLANK_CONSTRAINTS[column] }
      );

      const index = form.values.constraints.resources.findIndex(
        (resource) => resource.id === resourceId
      );

      form.setFieldValue(
        `constraints.resources.${index}.constraints.${column}`,
        newConstraints
      );
      debouncedTrigger();
    };

  const handleClear = (column: "never_work_masks" | "always_work_masks") => {
    const index = form.values.constraints.resources.findIndex(
      (resource) => resource.id === resourceId
    );
    form.setFieldValue(
      `constraints.resources.${index}.constraints.${column}`,
      BLANK_CONSTRAINTS[column]
    );
    form.validate();
  };

  return (
    <>
      <Card shadow="sm" padding="lg" style={{ marginBottom: "1rem" }}>
        <Grid>
          <Grid.Col span={12}>
            <Group justify="space-between">
              <Text fw={500} size="lg">
                Always Work Times
              </Text>
              <Button
                variant="outline"
                size="xs"
                onClick={() => handleClear("always_work_masks")}
              >
                Clear
              </Button>
            </Group>
          </Grid.Col>
          <Grid.Col span={12}>
            <ConstraintCalendar
              field={`always_work_masks`}
              resourceId={resourceId}
              onSelectChange={createOnSelectChange("always_work_masks")}
              color="lightblue"
            />
          </Grid.Col>
        </Grid>
      </Card>

      <Card shadow="sm" padding="lg" style={{ marginTop: "1rem" }}>
        <Grid>
          <Grid.Col span={12}>
            <Group justify="space-between">
              <Text fw={500} size="lg">
                Never Work Times
              </Text>
              <Button
                variant="outline"
                size="xs"
                onClick={() => handleClear("never_work_masks")}
              >
                Clear
              </Button>
            </Group>
          </Grid.Col>
          <Grid.Col span={12}>
            <ConstraintCalendar
              field={`never_work_masks`}
              resourceId={resourceId}
              onSelectChange={createOnSelectChange("never_work_masks")}
              color="rgba(242, 107, 44, 0.5)"
            />
          </Grid.Col>
        </Grid>
      </Card>
    </>
  );
};
