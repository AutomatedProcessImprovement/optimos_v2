import { Box, Card, Divider, Group, rem, Text } from "@mantine/core";
import { Dropzone, DropzoneProps, IMAGE_MIME_TYPE } from "@mantine/dropzone";
import { Description } from "@mui/icons-material";
import {
  IconUpload,
  IconX,
  IconPhoto,
  IconAdjustments,
  IconSchema,
  IconFile,
  IconFileUpload,
} from "@tabler/icons-react";
import React, { FC } from "react";
import { addAsset, addAssets, AssetType } from "../redux/slices/assetsSlice";
import { fileToAsset, unzipFile } from "../util/fileHelpers";
import { useDispatch, useSelector } from "react-redux";
import { showError } from "../util/helpers";
import { selectAssets } from "../redux/selectors/assetSelectors";
import AssetCard from "./AssetCard";

export const AssetsView = () => {
  const dispatch = useDispatch();
  const addAssetFromFile = (type: AssetType) => async (files: File[]) => {
    for (const file of files) {
      if (file.type === "application/zip") {
        const [assets, errs] = await unzipFile(file);
        errs.forEach((e) => showError(e));
        dispatch(addAssets(assets));
      } else {
        try {
          const asset = await fileToAsset(file);
          dispatch(addAsset(asset));
        } catch (e) {
          showError(e);
        }
      }
    }
  };

  const assets = useSelector(selectAssets);

  return (
    <Box>
      <Text size="lg" fw={500}>
        Assets
      </Text>

      {assets.map((asset) => (
        <AssetCard key={asset.id} asset={asset} />
      ))}

      <Divider my="md" />
      <CustomDropzone
        onDrop={addAssetFromFile(AssetType.OPTIMOS_CONSTRAINTS)}
        label="Upload Asset"
        mimeTypes={{
          "application/json": [],
          "application/xml": [".bpmn"],
          "application/zip": [],
        }}
        description=".json, .bpmn, .zip"
        icon={
          <IconFileUpload
            style={{
              width: rem(52),
              height: rem(52),
              color: "var(--mantine-color-blue-6)",
            }}
            stroke={1.5}
          />
        }
      />
    </Box>
  );
};
type CustomDropzoneProps = {
  label: string;
  mimeTypes: DropzoneProps["accept"];
  icon?: React.ReactNode;
  description?: string;
  onDrop?: (files: File[]) => void;
};

const CustomDropzone: FC<CustomDropzoneProps> = ({
  label,
  mimeTypes,
  icon,
  description,
  onDrop,
}) => {
  return (
    <Dropzone
      onDrop={(files) => onDrop?.(files)}
      maxSize={1 * 1024 ** 2}
      accept={mimeTypes}
    >
      <Group
        justify="center"
        gap="xl"
        mih={100}
        style={{ pointerEvents: "none" }}
      >
        <Dropzone.Accept>
          <IconUpload
            style={{
              width: rem(52),
              height: rem(52),
              color: "var(--mantine-color-blue-6)",
            }}
            stroke={1.5}
          />
        </Dropzone.Accept>
        <Dropzone.Reject>
          <IconX
            style={{
              width: rem(52),
              height: rem(52),
              color: "var(--mantine-color-red-6)",
            }}
            stroke={1.5}
          />
        </Dropzone.Reject>
        <Dropzone.Idle>{icon}</Dropzone.Idle>

        <div>
          <Text size="l" inline ta="center">
            {label}
          </Text>
          <Text size="xs" c="dimmed" inline mt={7} ta="center">
            {description}
          </Text>
        </div>
      </Group>
    </Dropzone>
  );
};
