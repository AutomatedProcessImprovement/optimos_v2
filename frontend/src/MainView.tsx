import React from "react";
import { AppShell, Card, Text, Box, Burger } from "@mantine/core";
import { ParameterEditor } from "./parameterEditor/ParameterEditor";
import { Button } from "@mantine/core";
import { useDisclosure } from "@mantine/hooks";

export const MainView = () => {
  const [leftOpened, { toggle: toggleLeft }] = useDisclosure(true);
  const [rightOpened, { toggle: toggleRight }] = useDisclosure(true);

  return (
    <AppShell
      padding="md"
      header={{ height: 60 }}
      navbar={{
        width: leftOpened ? 300 : 60,
        breakpoint: "sm",
        collapsed: { mobile: !leftOpened },
      }}
      aside={{
        width: rightOpened ? 300 : 60,
        breakpoint: "sm",
        collapsed: { mobile: !rightOpened },
      }}
    >
      {/* Header */}
      <AppShell.Header p="md" h={60} display="flex" ta="center">
        <Text size="xl" fw={500}>
          Optimos V2
        </Text>
      </AppShell.Header>

      {/* Left Sidebar - Navbar */}
      <AppShell.Navbar p="md">
        <Burger opened={leftOpened} onClick={toggleLeft} size="sm" />
        <Box>
          {leftOpened && (
            <Box>
              <Text size="lg" fw={500}>
                Assets
              </Text>
              {[1, 2, 3].map((item) => (
                <Card
                  key={item}
                  shadow="sm"
                  p="lg"
                  radius="md"
                  withBorder
                  mb="sm"
                >
                  <Text>Asset {item}</Text>
                </Card>
              ))}
            </Box>
          )}
        </Box>
      </AppShell.Navbar>

      {/* Main Editor Section */}
      <AppShell.Main>
        <Box p="md" style={{ textAlign: "center", height: "100%" }}>
          <ParameterEditor />
        </Box>
      </AppShell.Main>

      {/* Right Sidebar - Aside */}
      <AppShell.Aside p="md">
        <Burger opened={rightOpened} onClick={toggleRight} size="sm" />
        <Box>
          {rightOpened && (
            <Box>
              <Text size="lg" fw={500}>
                Outputs
              </Text>
              {[1, 2, 3].map((item) => (
                <Card
                  key={item}
                  shadow="sm"
                  p="lg"
                  radius="md"
                  withBorder
                  mb="sm"
                >
                  <Text>Output {item}</Text>
                </Card>
              ))}
            </Box>
          )}
        </Box>
      </AppShell.Aside>
    </AppShell>
  );
};
