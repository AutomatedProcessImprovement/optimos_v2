import { notifications } from "@mantine/notifications";
import { ErrorIcon } from "./ErrorIcon";

export function formatDate(date: Date) {
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  const day = date.getDate();

  const hour = date.getHours();
  const minute = date.getMinutes();

  const monthString = month.toString().padStart(2, "0");
  const dayString = day.toString().padStart(2, "0");

  const hourString = hour.toString().padStart(2, "0");
  const minuteString = minute.toString().padStart(2, "0");

  return `${year}-${monthString}-${dayString}T${hourString}:${minuteString}`;
}
export function makeTitleCase(str: string) {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

export const showError = (message: string) =>
  notifications.show({
    title: "An Error Occurred",
    message,
    color: "red",
    icon: ErrorIcon({}),
  });

export const showSuccess = (message: string) =>
  notifications.show({
    title: "Success",
    message,
    color: "green",
  });
