import { useEffect, useState } from "react";

const useJsonFile = <T extends Object>(jsonFile: File | Blob | null): { jsonData?: T; error?: string } => {
  const [jsonData, setJsonData] = useState<T>();
  const [error, setError] = useState<string>();

  useEffect(() => {
    if (jsonFile !== null) {
      const jsonFileReader = new FileReader();
      jsonFileReader.readAsText(jsonFile, "UTF-8");
      jsonFileReader.onload = (e) => {
        if (e.target?.result && typeof e.target?.result === "string") {
          try {
            const rawData = JSON.parse(e.target.result);
            setJsonData(rawData);
            setError(undefined);
          } catch (e) {
            setError(String(e));
          }
        }
      };
    }
  }, [jsonFile]);
  return { jsonData: jsonData as T, error };
};

export default useJsonFile;
