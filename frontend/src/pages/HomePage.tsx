import React from "react";
import { Box } from "@mantine/core";
import { ParameterEditor } from "../parameterEditor/ParameterEditor";

export const HomePage = () => (
  <Box p="md" style={{ textAlign: "center", height: "100%" }}>
    <ParameterEditor />
  </Box>
);
