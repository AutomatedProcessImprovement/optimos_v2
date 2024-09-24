import React, { useCallback } from "react";
import { Provider, useDispatch, useSelector } from "react-redux";
import { PersistGate } from "redux-persist/integration/react";
import { persistor, store } from "./redux/store";
import { ParameterEditor } from "./parameterEditor/ParameterEditor";
import "@mantine/core/styles.css";
import "@mantine/dropzone/styles.css";
import "@mantine/notifications/styles.css";
import { Notifications } from "@mantine/notifications";

import { HomePage } from "./pages/HomePage";
import {
  AppShell,
  Box,
  Burger,
  Button,
  createTheme,
  Group,
  MantineProvider,
  Text,
  UnstyledButton,
} from "@mantine/core";

import {
  createBrowserRouter,
  Link,
  Outlet,
  RouterProvider,
  useNavigate,
} from "react-router-dom";
import { router } from "./router";
import { AssetsView } from "./components/AssetsView";
import { OutputView } from "./components/OutputView";
import {
  selectLeftPanelOpen,
  selectRightPanelOpen,
} from "./redux/selectors/uiStateSelectors";
import {
  deselectAssets,
  setSidePanel,
  toggleSidePanel,
} from "./redux/slices/uiStateSlice";
import { PURGE, purgeStoredState } from "redux-persist";

export const Root = () => {
  const leftOpened = useSelector(selectLeftPanelOpen);
  const rightOpened = useSelector(selectRightPanelOpen);
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const goHome = useCallback(() => {
    dispatch(deselectAssets());
    dispatch(setSidePanel({ side: "left", open: true }));
    dispatch(setSidePanel({ side: "right", open: false }));
    navigate("/");
  }, [dispatch, navigate]);
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
        <Group justify="space-between" w="100%">
          <UnstyledButton onClick={goHome}>
            <Text size="xl" fw={500}>
              Optimos V2
            </Text>
          </UnstyledButton>
          <Group ml="xl" gap={0} visibleFrom="sm">
            <Button variant="white" onClick={goHome}>
              Start new Optimization
            </Button>
            <Button
              variant="white"
              onClick={async () => {
                await persistor.purge();
                navigate("/");
              }}
              color="red"
            >
              Clear Data
            </Button>
          </Group>
        </Group>
      </AppShell.Header>

      {/* Left Sidebar - Navbar */}
      <AppShell.Navbar p="md">
        <Burger
          opened={leftOpened}
          onClick={() => dispatch(toggleSidePanel("left"))}
          size="sm"
        />
        <Box>{leftOpened && <AssetsView />}</Box>
      </AppShell.Navbar>

      {/* Main Editor Section */}
      <AppShell.Main>
        <Outlet />
      </AppShell.Main>

      {/* Right Sidebar - Aside */}
      <AppShell.Aside p="md">
        <Burger
          opened={rightOpened}
          onClick={() => dispatch(toggleSidePanel("right"))}
          size="sm"
        />
        {rightOpened && <OutputView />}
      </AppShell.Aside>
    </AppShell>
  );
};
