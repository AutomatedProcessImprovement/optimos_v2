import {
  Person as PersonIcon,
  PrecisionManufacturing as PrecisionManufacturingIcon,
  ContentPaste as ContentPasteIcon,
  ContentPasteGo as ContentPasteGoIcon,
  RestartAlt as RestartAltIcon,
  Event as EventIcon,
} from "@mui/icons-material";

import {
  Button,
  ButtonGroup,
  Card,
  Divider,
  Grid,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  TextField,
  Typography,
} from "@mui/material";

import type { FC } from "react";
import React, { useEffect } from "react";
import { ResourceCopyDialog } from "./ResourceCopyDialog";
import {
  applyConstraintsToAllResources,
  applyConstraintsToResources,
  applyTimetableToAllResources,
  resetResourceConstraintsToBlank,
  resetResourceConstraintsToNineToFive,
} from "../helpers";
import type { MasterFormData } from "../hooks/useMasterFormData";
import { useMasterFormContext } from "../hooks/useFormContext";

export type ResourceSelectionProps = {
  currResourceId?: string;
  updateCurrCalendar: (id: string) => void;
};

export const ResourceSelection: FC<ResourceSelectionProps> = ({
  currResourceId,
  updateCurrCalendar,
}) => {
  const form = useMasterFormContext();
  const resources = form.values?.constraints?.resources ?? [];
  useEffect(() => {}, [form.values?.constraints?.resources]);
  const [searchTerm, setSearchTerm] = React.useState("");
  const [searchResults, setSearchResults] = React.useState(resources);
  const [modalOpen, setModalOpen] = React.useState(false);

  useEffect(() => {
    const results = resources.filter((calendar) =>
      calendar.id.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setSearchResults(results);
  }, [resources, searchTerm]);

  return (
    <>
      <Card
        elevation={5}
        sx={{
          p: 2,
        }}
      >
        <Grid item xs={12}>
          <Typography variant="h6">Resources</Typography>
        </Grid>
        <Grid
          container
          direction={"row"}
          justifyContent={"space-around"}
          alignItems={"stretch"}
        >
          <Grid
            item
            xs={5}
            sx={{
              p: 2,
            }}
          >
            <TextField
              sx={{
                width: "100%",
                mb: 1,
              }}
              label="Search"
              type="search"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <List
              sx={{
                overflowY: "scroll",
                height: "300px",
              }}
            >
              {searchResults.map((item) => {
                const isSelected = currResourceId === item.id;
                return (
                  <ListItemButton
                    selected={isSelected}
                    key={item.id}
                    onClick={() => updateCurrCalendar(item.id)}
                  >
                    <ListItemIcon>
                      {item.constraints.global_constraints?.is_human ? (
                        <PersonIcon />
                      ) : (
                        <PrecisionManufacturingIcon />
                      )}
                    </ListItemIcon>
                    <ListItemText>{item.id}</ListItemText>
                  </ListItemButton>
                );
              })}
            </List>
          </Grid>

          <Divider orientation="vertical" flexItem variant="middle" />

          <Grid
            item
            container
            xs={5}
            justifyContent={"center"}
            alignItems={"center"}
          >
            <Grid
              container
              width={"100%"}
              height={"80%"}
              justifyContent={"center"}
              alignItems={"center"}
            >
              <Grid item width={"100%"}>
                <Typography variant="caption">COPY ALL CONSTRAINTS</Typography>
                <ButtonGroup fullWidth>
                  <Button
                    variant="outlined"
                    disabled={!currResourceId}
                    onClick={() => {
                      const newResources = applyConstraintsToAllResources(
                        resources,
                        currResourceId!
                      );
                      form.setValue("constraints.resources", newResources, {
                        shouldDirty: true,
                        shouldValidate: false,
                      });
                      form.trigger();
                    }}
                    startIcon={<ContentPasteIcon />}
                  >
                    Apply to All
                  </Button>
                  <Button
                    disabled={!currResourceId}
                    variant="outlined"
                    onClick={() => setModalOpen(true)}
                    startIcon={<ContentPasteGoIcon />}
                  >
                    Copy to...
                  </Button>
                </ButtonGroup>
              </Grid>
              <Grid item width={"100%"}>
                <Typography variant="caption">
                  COPY ONLY TIME CONSTRAINTS
                </Typography>
                <ButtonGroup fullWidth>
                  <Button
                    variant="outlined"
                    disabled={!currResourceId}
                    onClick={() => {
                      const newResources = applyTimetableToAllResources(
                        resources,
                        currResourceId!
                      );

                      form.setValue("constraints.resources", newResources, {
                        shouldDirty: true,
                        shouldValidate: false,
                      });
                      form.trigger();
                    }}
                    startIcon={<ContentPasteIcon />}
                  >
                    Apply time constraints to All
                  </Button>
                </ButtonGroup>
              </Grid>
              {/* <Grid item alignSelf={"center"} width={"80%"}>
                <Divider variant="middle" orientation="horizontal" />
              </Grid> */}
              <Grid item width={"100%"}>
                <Typography variant="caption">RESET CONSTRAINTS</Typography>
                <ButtonGroup orientation="vertical" fullWidth>
                  <Button
                    disabled={!currResourceId}
                    variant="outlined"
                    startIcon={<RestartAltIcon />}
                    onClick={() => {
                      const newResources = resetResourceConstraintsToBlank(
                        resources,
                        currResourceId!
                      );
                      form.setValue("constraints.resources", newResources, {
                        shouldDirty: true,
                        shouldTouch: true,
                        shouldValidate: false,
                      });
                      form.trigger();
                    }}
                  >
                    Reset to blank constraints
                  </Button>
                  <Button
                    disabled={!currResourceId}
                    variant="outlined"
                    startIcon={<EventIcon />}
                    onClick={() => {
                      const newResources = resetResourceConstraintsToNineToFive(
                        resources,
                        currResourceId!
                      );

                      form.setValue("constraints.resources", newResources, {
                        shouldDirty: true,
                        shouldTouch: true,
                        shouldValidate: false,
                      });
                      form.trigger();
                    }}
                  >
                    Reset to 9-5 working times
                  </Button>
                </ButtonGroup>
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </Card>
      <ResourceCopyDialog
        open={modalOpen}
        onClose={(selectedIds) => {
          setModalOpen(false);
          const newResources = applyConstraintsToResources(
            resources,
            currResourceId!,
            selectedIds
          );
          form.setValue("constraints.resources", newResources, {
            shouldDirty: true,
            shouldValidate: true,
          });
        }}
        selectedValue={currResourceId ?? ""}
        resources={resources}
      />
    </>
  );
};
