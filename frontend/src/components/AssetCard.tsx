import {
  Card,
  Text,
  Group,
  ActionIcon,
  Badge,
  useMantineTheme,
  Stack,
} from "@mantine/core";
import {
  IconTrash,
  IconFileDescription,
  IconSettings,
  IconTools,
  IconCalendar,
} from "@tabler/icons-react"; // Importing relevant icons
import { Asset, AssetType, removeAsset } from "../redux/slices/assetsSlice";
import React, { useCallback, useMemo } from "react";
import { useDispatch, useSelector } from "react-redux";
import { deselectAsset, selectAsset } from "../redux/slices/uiStateSlice";
import { selectIsAssetSelected } from "../redux/selectors/assetSelectors";
import { RootState } from "../redux/store";

type AssetCardProps = {
  asset: Asset;
};

// Function to get the appropriate icon based on asset type
const getIcon = (type: AssetType) => {
  switch (type) {
    case AssetType.BPMN:
      return <IconFileDescription size={24} />;
    case AssetType.OPTIMOS_CONFIG:
      return <IconSettings size={24} />;
    case AssetType.OPTIMOS_CONSTRAINTS:
      return <IconTools size={24} />;
    case AssetType.TIMETABLE:
      return <IconCalendar size={24} />;
    default:
      return <IconFileDescription size={24} />;
  }
};

const getName = (type: AssetType) => {
  switch (type) {
    case AssetType.BPMN:
      return "BPMN";
    case AssetType.OPTIMOS_CONFIG:
      return "Optimos Config";
    case AssetType.OPTIMOS_CONSTRAINTS:
      return "Optimos Constraints";
    case AssetType.TIMETABLE:
      return "Timetable";
    default:
      return "Unknown";
  }
};

const AssetCard: React.FC<AssetCardProps> = ({ asset }) => {
  const dispatch = useDispatch();

  const isSelected = useSelector<RootState>((state) =>
    selectIsAssetSelected(state, asset.id)
  );

  const theme = useMantineTheme();

  return (
    <Card
      shadow="sm"
      padding="md"
      radius="md"
      onClick={() =>
        isSelected
          ? dispatch(deselectAsset(asset.id))
          : dispatch(selectAsset(asset.id))
      }
      style={{
        border: isSelected ? `2px solid ${theme.colors.blue[6]}` : undefined,
        cursor: "pointer",
        transition: "border 0.2s ease",
        backgroundColor: isSelected ? theme.colors.blue[0] : theme.white,
      }}
    >
      <Group justify="space-between" align="center">
        <Group>
          {getIcon(asset.type)}
          <Stack gap={0}>
            <Text size="sm">{asset.name}</Text>
            <Badge color="gray" size="xs">
              {getName(asset.type)}
            </Badge>
          </Stack>
        </Group>
        <ActionIcon
          color="red"
          onClick={(e) => {
            e.stopPropagation(); // Prevent the click from triggering the selection
            dispatch(removeAsset(asset.id));
          }}
        >
          <IconTrash size={18} />
        </ActionIcon>
      </Group>
    </Card>
  );
};

export default AssetCard;
