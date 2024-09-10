import { useCallback, useMemo, type FC } from "react";
import { MasterFormData } from "../hooks/useMasterFormData";
import {
  Button,
  Card,
  CardActions,
  CardContent,
  CardHeader,
  Grid,
  IconButton,
  Typography,
} from "@mui/material";
import {
  Launch as LaunchIcon,
  Warning as WarningIcon,
  AutoFixHigh as AutoFixHighIcon,
  AutoFixNormal as AutoFixNormalIcon,
} from "@mui/icons-material";
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
      <Card elevation={5} sx={{ p: 2, mb: 3, width: "100%" }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Typography variant="h6" align="left">
                Constraint Validation
              </Typography>
            </Grid>
            <Grid item xs={12}>
              {!!convertedErrors.length && (
                <Typography variant="body1" align="left">
                  The following errors are still present in the constraints.
                  Please fix them before proceeding.
                </Typography>
              )}
              {!convertedErrors.length && (
                <Typography variant="body1" align="left">
                  No errors found in the constraints, you may start the
                  optimization below.
                </Typography>
              )}
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Grid container spacing={2} justifyContent={"center"}>
        {convertedErrors.map((error, index) => {
          return (
            <Grid item xs={11} key={index}>
              <Card elevation={5}>
                <CardHeader
                  avatar={<WarningIcon />}
                  title={`Issue in ${error.humanReadableFieldName}`}
                  subheader={error.humanReadablePath}
                  action={
                    <IconButton
                      aria-label="go to issue"
                      onClick={() => navigate(error.link)}
                    >
                      <LaunchIcon />
                    </IconButton>
                  }
                ></CardHeader>
                <CardContent>
                  <Typography variant="body2" align="left">
                    <i>{error.message}</i>
                  </Typography>
                </CardContent>
                <CardActions>
                  {error.autoFixes.map((fix, index) => {
                    return (
                      <Button
                        onClick={() => fix.action(getValues, setValueVerify)}
                        variant={!index ? "contained" : "text"}
                        size="small"
                        key={index}
                        startIcon={
                          !index ? <AutoFixHighIcon /> : <AutoFixNormalIcon />
                        }
                      >
                        {fix.title}
                      </Button>
                    );
                  })}
                </CardActions>
              </Card>
            </Grid>
          );
        })}
      </Grid>
    </>
  );
};
