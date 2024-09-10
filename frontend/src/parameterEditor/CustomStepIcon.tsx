import { FC } from "react";
import { TABS } from "../hooks/useTabVisibility";
import { Badge, useTheme } from "@mui/material";
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
import { useFormContext, useFormState } from "react-hook-form";

type CustomStepIconProps = {
  activeStep: TABS;
  currentTab: TABS;
};

export const CustomStepIcon: FC<CustomStepIconProps> = ({
  currentTab,
  activeStep,
}) => {
  const theme = useTheme();
  const activeColor = theme.palette.info.dark;
  const successColor = theme.palette.success.light;
  const errorColor = theme.palette.error.light;

  const isActiveStep = activeStep === currentTab;
  const styles = isActiveStep ? { color: activeColor } : {};
  const form = useFormContext<MasterFormData>();
  const { isValid, isValidating } = useFormState({ control: form.control });

  switch (currentTab) {
    case TABS.GLOBAL_CONSTRAINTS:
      return <BuildIcon style={styles} />;

    case TABS.SCENARIO_CONSTRAINTS:
      return <SettingsIcon style={styles} />;

    case TABS.RESOURCE_CONSTRAINTS:
      return <GroupsIcon style={styles} />;

    case TABS.VALIDATION_RESULTS:
      let BadgeIcon: SvgIconComponent = CheckCircleIcon;
      let color = successColor;

      if (isValidating) {
        BadgeIcon = AutorenewIcon;
        color = activeColor;
      } else if (!isValid) {
        BadgeIcon = CancelIcon;
        color = errorColor;
      }

      return (
        <Badge
          badgeContent={<BadgeIcon style={{ color }} />}
          overlap="circular"
        >
          <WarningIcon style={styles} />
        </Badge>
      );

    default:
      return <></>;
  }
};
