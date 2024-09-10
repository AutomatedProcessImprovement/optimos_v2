import { useCallback, useContext, useEffect, useRef, useState } from "react";
import { UserContext } from "~/routes/contexts";
import { SelectedAssetsContext } from "~/routes/projects.$projectId.$processingType/contexts";
import type { Asset, AssetType } from "~/services/assets";
import { getAsset } from "~/services/assets";
import type { File, FileType } from "~/services/files";
import { getFile, getFileContent } from "~/services/files";

export const useFileFromAsset = (
  assetType: AssetType,
  fileType: FileType
): [Blob | null, React.RefObject<HTMLInputElement>] => {
  const selectedAssetsIdsRef = useRef<HTMLInputElement>(null);

  const user = useContext(UserContext);
  const selectedAssets = useContext(SelectedAssetsContext);
  const [file, setFile] = useState<Blob | null>(null);
  const fetchAsset = useCallback(async () => {
    const simulationModel = selectedAssets.find((asset) => asset.type === assetType);
    if (simulationModel && user?.token) {
      // this call populates the files field with the file objects, so we can find a BPMN model file and fetch its content
      const asset = await getAsset(simulationModel.id, user?.token, false);
      const fileId = asset?.files?.find((file) => file.type === fileType)?.id;
      if (fileId) {
        const file = await getFileContent(fileId, user?.token);
        setFile(file);
      } else {
        setFile(null);
      }
    } else {
      setFile(null);
    }
  }, [assetType, selectedAssets, user?.token]);

  useEffect(() => {
    if (selectedAssetsIdsRef.current) {
      selectedAssetsIdsRef.current!.value = selectedAssets.map((asset) => asset.id).join(",");
    }
    fetchAsset();
  }, [selectedAssets, fetchAsset]);

  return [file, selectedAssetsIdsRef];
};
