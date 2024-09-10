import { useCallback, useMemo, type FC } from "react";
import { MasterFormData } from "../hooks/useMasterFormData";
import {
  Card,
  Grid,
  Text,
  Group,
  Button,
  ActionIcon,
  ThemeIcon,
} from "@mantine/core";
import {
  IconAlertCircle,
  IconExternalLink,
  IconSettingsAutomation,
  IconAdjustments,
} from "@tabler/icons-react"; //
import { convertError } from "./validationHelper";
import React from "react";
import { useMasterFormContext } from "../hooks/useFormContext";
import jsonpath from "jsonpath";

type ValidationTabProps = {};
export const ValidationTab: FC<ValidationTabProps> = (props) => {
  const { errors, getValues, setFieldValue, validate } = useMasterFormContext();
  const setValueVerify = useCallback(
    (
      key: Parameters<typeof setFieldValue>[0],
      value: Parameters<typeof setFieldValue>[1]
    ) => {
      setFieldValue(key, value);
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    []
  );

  const getSingleValue = useCallback(
    (key: string) => jsonpath.value(getValues(), key),
    [getValues]
  );

  const convertedErrors = useMemo(
    () => convertError(errors, getValues()),
    [errors, getValues]
  );

  return (
    <>
      <Card shadow="sm" padding="lg" style={{ width: "100%" }}>
        <Grid>
          <Grid.Col span={12}>
            <Text size="lg" fw={500} ta="left">
              Constraint Validation
            </Text>
          </Grid.Col>
          <Grid.Col span={12}>
            {!!convertedErrors.length ? (
              <Text>
                The following errors are still present in the constraints.
                Please fix them before proceeding.
              </Text>
            ) : (
              <Text>
                No errors found in the constraints, you may start the
                optimization below.
              </Text>
            )}
          </Grid.Col>
        </Grid>
      </Card>

      {convertedErrors.map((error, index) => (
        <Grid.Col span={11} key={index}>
          <Card shadow="sm">
            <Group align="center" mb="sm">
              <ThemeIcon variant="light" color="yellow" size="lg">
                <IconAlertCircle size={24} />
              </ThemeIcon>
              <Text size="md" weight={500}>
                Issue in {error.humanReadableFieldName}
              </Text>
              <Text size="sm" color="dimmed">
                {error.humanReadablePath}
              </Text>
              <ActionIcon onClick={() => navigate(error.link)}>
                <IconExternalLink size={18} />
              </ActionIcon>
            </Group>

            <Text size="sm" mb="md" style={{ fontStyle: "italic" }}>
              {error.message}
            </Text>

            <Group spacing="xs">
              {error.autoFixes.map((fix, index) => (
                <Button
                  onClick={() => fix.action(getValues, setValueVerify)}
                  variant={index === 0 ? "filled" : "outline"}
                  size="xs"
                  key={index}
                  leftSection={
                    index === 0 ? (
                      <IconSettingsAutomation size={16} />
                    ) : (
                      <IconAdjustments size={16} />
                    )
                  }
                >
                  {fix.title}
                </Button>
              ))}
            </Group>
          </Card>
        </Grid.Col>
      ))}
    </>
  );
};
