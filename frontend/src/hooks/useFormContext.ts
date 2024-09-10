import { createFormContext } from "@mantine/form";
import { MasterFormData } from "./useMasterFormData";

export const [MasterFormProvider, useMasterFormContext, useMasterForm] =
  createFormContext<MasterFormData>();
