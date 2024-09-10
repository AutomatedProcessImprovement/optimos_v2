import {
  Person as PersonIcon,
  PrecisionManufacturing as PrecisionManufacturingIcon,
  ContentPaste as ContentPasteIcon,
  ContentPasteGo as ContentPasteGoIcon,
  RestartAlt as RestartAltIcon,
  Event as EventIcon,
} from "@mui/icons-material";

import {
  Card,
  Grid,
  Text,
  TextInput,
  List,
  Button,
  Divider,
  Group,
  Checkbox,
  Select,
  ButtonGroup,
} from "@mantine/core";

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
      <Card shadow="sm" padding="lg">
        <Grid>
          <Grid.Col span={12}>
            <Text size="lg" fw={500} ta={"left"}>
              Resources
            </Text>
          </Grid.Col>

          <Grid.Col span={5}>
            <TextInput
              label="Search"
              placeholder="Search resources"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.currentTarget.value)}
              mb="sm"
              width={"100%"}
            />
            <List
              style={{
                overflowY: "auto",
                maxHeight: 300,
              }}
            >
              {searchResults.map((item) => (
                <List.Item
                  key={item.id}
                  onClick={() => updateCurrCalendar(item.id)}
                  style={{
                    cursor: "pointer",
                    backgroundColor:
                      currResourceId === item.id ? "#f0f0f0" : "transparent",
                  }}
                >
                  {item.constraints.global_constraints?.is_human ? (
                    <Checkbox
                      checked={true}
                      label={item.id}
                      icon={PersonIcon}
                    />
                  ) : (
                    <Checkbox
                      checked={true}
                      label={item.id}
                      icon={PrecisionManufacturingIcon}
                    />
                  )}
                </List.Item>
              ))}
            </List>
          </Grid.Col>

          <Divider orientation="vertical" mx="xl" />

          <Grid.Col span={5}>
            <Group
              direction="column"
              spacing="md"
              align="center"
              style={{ height: "100%" }}
            >
              <Text size="sm">COPY ALL CONSTRAINTS</Text>
              <ButtonGroup>
                <Button
                  variant="outline"
                  disabled={!currResourceId}
                  onClick={() => {
                    const newResources = applyConstraintsToAllResources(
                      resources,
                      currResourceId!
                    );
                    form.setFieldValue("constraints.resources", newResources);
                  }}
                >
                  Apply to All
                </Button>
                <Button
                  variant="outline"
                  disabled={!currResourceId}
                  onClick={() => setModalOpen(true)}
                >
                  Copy to...
                </Button>
              </ButtonGroup>

              <Text size="sm">COPY ONLY TIME CONSTRAINTS</Text>
              <ButtonGroup>
                <Button
                  variant="outline"
                  disabled={!currResourceId}
                  onClick={() => {
                    const newResources = applyTimetableToAllResources(
                      resources,
                      currResourceId!
                    );
                    form.setFieldValue("constraints.resources", newResources);
                  }}
                >
                  Apply time constraints to All
                </Button>
              </ButtonGroup>

              <Text size="sm">RESET CONSTRAINTS</Text>
              <ButtonGroup orientation="vertical">
                <Button
                  variant="outline"
                  disabled={!currResourceId}
                  onClick={() => {
                    const newResources = resetResourceConstraintsToBlank(
                      resources,
                      currResourceId!
                    );
                    form.setFieldValue("constraints.resources", newResources);
                  }}
                >
                  Reset to blank constraints
                </Button>
                <Button
                  variant="outline"
                  disabled={!currResourceId}
                  onClick={() => {
                    const newResources = resetResourceConstraintsToNineToFive(
                      resources,
                      currResourceId!
                    );
                    form.setFieldValue("constraints.resources", newResources);
                  }}
                >
                  Reset to 9-5 working times
                </Button>
              </ButtonGroup>
            </Group>
          </Grid.Col>
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
          form.setFieldValue("constraints.resources", newResources);
        }}
        selectedValue={currResourceId ?? ""}
        resources={resources}
      />
    </>
  );
};
