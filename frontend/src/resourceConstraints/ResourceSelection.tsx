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
  Stack,
  Avatar,
  ScrollArea,
} from "@mantine/core";

import type { FC } from "react";
import React, { useEffect, useMemo, useState } from "react";
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

  const [searchTerm, setSearchTerm] = useState("");
  const [modalOpen, setModalOpen] = useState(false);

  const searchResults = useMemo(() => {
    return resources.filter((resource) =>
      resource.id.toLowerCase().includes(searchTerm.toLowerCase())
    );
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
            <ScrollArea type="always" h={200} offsetScrollbars>
              <Stack gap="sm">
                {searchResults.map((item) => (
                  <Card
                    withBorder
                    key={item.id}
                    onClick={() => updateCurrCalendar(item.id)}
                    style={{
                      cursor: "pointer",
                      backgroundColor:
                        currResourceId === item.id ? "lightblue" : "white",
                    }}
                    p="sm"
                  >
                    <Group>
                      {item.constraints.global_constraints?.is_human ? (
                        <Avatar color="blue" radius="sm">
                          <PersonIcon />
                        </Avatar>
                      ) : (
                        <Avatar color="blue" radius="sm">
                          <PrecisionManufacturingIcon />
                        </Avatar>
                      )}
                      <Text>{item.id}</Text>
                    </Group>
                  </Card>
                ))}
              </Stack>
            </ScrollArea>
          </Grid.Col>

          <Divider orientation="vertical" mx="xl" />

          <Grid.Col span={5}>
            <Stack gap="md" align="center" style={{ height: "100%" }}>
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
            </Stack>
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
