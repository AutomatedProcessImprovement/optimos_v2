import { FC } from "react";
import { TABS } from "../hooks/useTabVisibility";

import {
  Groups as GroupsIcon,
  BarChart as BarChartIcon,
  Settings as SettingsIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Build as BuildIcon,
  Warning as WarningIcon,
  Autorenew as AutorenewIcon,
  SvgIconComponent,
} from "@mui/icons-material";
import { MasterFormData } from "../hooks/useMasterFormData";
import React from "react";

import { Badge, useMantineTheme } from "@mantine/core";
import { useMasterFormContext } from "../hooks/useFormContext";

type CustomStepIconProps = {
  activeStep: TABS;
  currentTab: TABS;
};

export const CustomStepIcon: FC<CustomStepIconProps> = ({
  currentTab,
  activeStep,
}) => {
  const theme = useMantineTheme();
  const activeColor = theme.colors[theme.primaryColor][6];
  const successColor = theme.colors.green[8];
  const errorColor = theme.colors.red[6];

  const isActiveStep = activeStep === currentTab;
  const styles = isActiveStep ? { color: activeColor } : {};
  const form = useMasterFormContext();
  const isValid = form.isValid();

  switch (currentTab) {
    case TABS.GLOBAL_CONSTRAINTS:
      return <BuildIcon style={styles} />;

    case TABS.SCENARIO_CONSTRAINTS:
      return <SettingsIcon style={styles} />;

    case TABS.RESOURCE_CONSTRAINTS:
      return <GroupsIcon style={styles} />;

    case TABS.VALIDATION_RESULTS:
      let BadgeIcon: SvgIconComponent = CheckCircleIcon;

      if (!isValid) {
        BadgeIcon = CancelIcon;
        styles.color = errorColor;
      } else {
        styles.color = successColor;
      }

      return <BadgeIcon style={styles} />;

    default:
      return <></>;
  }
};
