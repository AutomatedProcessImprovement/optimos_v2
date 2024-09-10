import YAML from "yaml";
import { useEffect, useState } from "react";

export const useYAMLFile = <T>(yamlFile: File | Blob | null) => {
  const [yamlData, setyamlData] = useState<T>();

  useEffect(() => {
    if (yamlFile !== null) {
      const yamlFileReader = new FileReader();
      yamlFileReader.readAsText(yamlFile, "UTF-8");
      yamlFileReader.onload = (e) => {
        if (e.target?.result && typeof e.target?.result === "string") {
          const rawData = YAML.parse(e.target.result);
          setyamlData(rawData);
        }
      };
    }
  }, [yamlFile]);
  return { yamlData };
};
