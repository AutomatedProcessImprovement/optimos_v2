import { useEffect, useState } from "react";

const useSimParamsJsonFile = (jsonFile: any) => {
  const [jsonData, setJsonData] = useState<SimJsonData>();

  useEffect(() => {
    if (jsonFile !== null && jsonFile !== "") {
      const jsonFileReader = new FileReader();
      jsonFileReader.readAsText(jsonFile, "UTF-8");
      jsonFileReader.onload = (e) => {
        if (e.target?.result && typeof e.target?.result === "string") {
          const rawData = JSON.parse(e.target.result);
          setJsonData(rawData);
        }
      };
    }
  }, [jsonFile]);
  return { jsonData };
};

export default useSimParamsJsonFile;
