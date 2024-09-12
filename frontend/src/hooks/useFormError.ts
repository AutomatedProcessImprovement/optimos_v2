import { useMemo } from "react";
import { Leaves, Paths } from "../types/paths";
import { useMasterFormContext } from "./useFormContext";
import { MasterFormData } from "./useMasterFormData";
import { getProperty } from "dot-prop";

export const useFormError = (path: string) => {
  const form = useMasterFormContext();

  const error = useMemo(() => {
    const pathWithBrackets = path.replace(/\.(\d+)\./g, "[$1].");
    const error = getProperty(form.errors, pathWithBrackets);
    return error ? error : null;
  }, [form.errors, path]);

  return error;
};
