import React, { useState } from "react";
import {
  Box,
  Card,
  CardContent,
  IconButton,
  Typography,
  Divider,
} from "@mui/material";
import { ChevronLeft, ChevronRight } from "@mui/icons-material";
import { ParameterEditor } from "./parameterEditor/ParameterEditor";
export const MainView = () => {
  const [leftOpen, setLeftOpen] = useState(true);
  const [rightOpen, setRightOpen] = useState(true);

  const toggleLeft = () => setLeftOpen(!leftOpen);
  const toggleRight = () => setRightOpen(!rightOpen);
  return (
    <Box display="flex" height="100vh">
      {/* Left Sidebar */}
      <Box
        sx={{
          width: leftOpen ? 300 : 50,
          bgcolor: "grey.200",
          p: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: leftOpen ? "flex-start" : "center",
          overflow: "auto",
          transition: "width 0.3s",
        }}
      >
        <IconButton onClick={toggleLeft}>
          {leftOpen ? <ChevronLeft /> : <ChevronRight />}
        </IconButton>
        {leftOpen && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Assets
            </Typography>
            {/* Asset Cards */}
            {[1, 2, 3].map((item) => (
              <Card key={item} sx={{ mb: 1 }}>
                <CardContent>
                  <Typography>Asset {item}</Typography>
                </CardContent>
              </Card>
            ))}
          </Box>
        )}
      </Box>

      {/* Editor */}
      <Box flexGrow={1} bgcolor="grey.100" p={2}>
        <ParameterEditor />
      </Box>

      {/* Right Sidebar */}
      <Box
        sx={{
          width: rightOpen ? 300 : 50,
          bgcolor: "grey.200",
          p: 1,
          display: "flex",
          flexDirection: "column",
          alignItems: rightOpen ? "flex-start" : "center",
          overflow: "auto",
          transition: "width 0.3s",
        }}
      >
        <IconButton onClick={toggleRight}>
          {rightOpen ? <ChevronRight /> : <ChevronLeft />}
        </IconButton>
        {rightOpen && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Outputs
            </Typography>
            {/* Output Cards */}
            {[1, 2, 3].map((item) => (
              <Card key={item} sx={{ mb: 1 }}>
                <CardContent>
                  <Typography>Output {item}</Typography>
                </CardContent>
              </Card>
            ))}
          </Box>
        )}
      </Box>
    </Box>
  );
};
