import type { MasterFormData } from "./useMasterFormData";
import { useMasterFormContext } from "./useFormContext";

export const useSimParamsWorkTimes = (resourceId: string, day?: string) => {
  const form = useMasterFormContext<MasterFormData>();
  const calendars = form.getValues().simulationParameters.resource_calendars;
  const workTimes = calendars.find(
    (calendar) => calendar.id === resourceId
  )?.time_periods;
  if (day) {
    return workTimes?.filter(
      (time) => time.from.toLocaleLowerCase() === day.toLocaleLowerCase()
    );
  } else {
    return workTimes;
  }
};

export const useSimParamsResourceIndex = (resourceId: string) => {
  const form = useMasterFormContext<MasterFormData>();
  const calendars = form.getValues().simulationParameters.resource_calendars;
  const index = calendars.findIndex((calendar) => calendar.id === resourceId);
  return index;
};
