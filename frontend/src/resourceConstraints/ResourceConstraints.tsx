import { ResourceSelection } from "./ResourceSelection";
import { Card, Grid, Text } from "@mantine/core";

import { useState, useEffect, useCallback } from "react";

import { ResourceConstraintsList } from "./ResourceConstraintsList";
import type { MasterFormData } from "../hooks/useMasterFormData";
import React from "react";
import { useMasterFormContext } from "../hooks/useFormContext";

interface ResourceCalendarsProps {}
const ResourceConstraints = (props: ResourceCalendarsProps) => {
  const [currResourceId, setCurrResourceId] = useState<string | undefined>();
  const form = useMasterFormContext();

  const resources = form.values?.constraints?.resources;

  useEffect(() => {}, [form.values?.constraints?.resources]);

  const updateCurrCalendar = (id?: string) => {
    setCurrResourceId(id);
  };

  useEffect(() => {
    if (currResourceId == null) {
      setCurrResourceId(resources?.length > 0 ? resources[0].id : undefined);
    }
  }, [currResourceId, resources]);

  return (
    <Grid style={{ width: "100%" }} gutter="md">
      <Grid.Col span={12}>
        <ResourceSelection
          currResourceId={currResourceId}
          updateCurrCalendar={updateCurrCalendar}
        />
      </Grid.Col>
      {currResourceId === undefined ? (
        <Grid gutter="md" w="100%">
          <Grid.Col span={12} p="md">
            <Card shadow="sm" padding="lg" w="100%">
              <Text>Please select the resource to see its configuration</Text>
            </Card>
          </Grid.Col>
        </Grid>
      ) : (
        <Grid.Col span={12} p="md">
          <ResourceConstraintsList currResourceId={currResourceId} />
        </Grid.Col>
      )}
    </Grid>
  );
};

export default ResourceConstraints;
