import React from "react";
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
import { toggleSidePanel } from "./redux/slices/uiStateSlice";

export const Root = () => {
  const leftOpened = useSelector(selectLeftPanelOpen);
  const rightOpened = useSelector(selectRightPanelOpen);
  const dispatch = useDispatch();
  const navigate = useNavigate();
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
        <UnstyledButton onClick={() => navigate("/")}>
          <Text size="xl" fw={500}>
            Optimos V2
          </Text>
        </UnstyledButton>
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
