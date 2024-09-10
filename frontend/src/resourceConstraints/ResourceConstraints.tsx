import { ResourceSelection } from "./ResourceSelection";
import { Grid, Typography } from "@mui/material";
import { useState, useEffect, useCallback } from "react";
import { useFieldArray, useFormContext, useWatch, type UseFormReturn } from "react-hook-form";

import type { ConsParams } from "~/shared/optimos_json_type";
import { ResourceConstraintsList } from "./ResourceConstraintsList";
import type { MasterFormData } from "../hooks/useMasterFormData";

interface ResourceCalendarsProps {}

const ResourceConstraints = (props: ResourceCalendarsProps) => {
  const form = useFormContext<MasterFormData>();
  const [currResourceId, setCurrResourceId] = useState<string>();

  const resources = useWatch({ control: form.control, name: "constraints.resources" });
  const updateCurrCalendar = (id?: string) => {
    // update index
    setCurrResourceId(id);
  };

  useEffect(() => {
    if (currResourceId == null) setCurrResourceId(resources.length > 0 ? resources[0].id : undefined);
  }, [currResourceId, resources]);

  return (
    <Grid container width="100%" spacing={2}>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <ResourceSelection currResourceId={currResourceId} updateCurrCalendar={updateCurrCalendar} />
        </Grid>
      </Grid>
      {currResourceId === undefined ? (
        <Grid item xs={12} sx={{ p: 2 }}>
          <Typography>Please select the resource to see its configuration</Typography>
        </Grid>
      ) : (
        <Grid item xs={12} sx={{ p: 2 }}>
          <ResourceConstraintsList currResourceId={currResourceId} />
        </Grid>
      )}
    </Grid>
  );
};

export default ResourceConstraints;
