export const formatNumber = (num: number, decimals = 2) => {
  return num.toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};

export const formatSeconds = (seconds?: number, includeHours = true) => {
  if (seconds === undefined) return "";

  const days = Math.floor(seconds / (24 * 60 * 60));
  const hours = Math.floor((seconds % (24 * 60 * 60)) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  const secondsLeft = Math.floor(seconds % 60);

  let result = "";
  if (includeHours && days > 0) {
    result += `${days}d `;
  }
  if (includeHours && hours > 0) {
    result += `${hours}h `;
  }
  if (minutes > 0 || hours > 0) {
    result += `${minutes}m `.padStart(4, "0");
  }
  result += `${secondsLeft}s`.padStart(3, "0");

  return result;
};

export const formatMilliseconds = (milliseconds?: number) =>
  formatSeconds(milliseconds ? milliseconds / 1000 : undefined);

export const formatHours = (hours?: number) => {
  if (hours === undefined) return "";
  return `${formatNumber(hours)}h`;
};

export const formatCurrency = (num?: number) => {
  if (num === undefined) return "";
  return num.toLocaleString(undefined, {
    style: "currency",
    currency: "USD",
  });
};

export const formatHourlyRate = (num?: number) => {
  if (num === undefined) return "";
  return `${formatCurrency(num)}/h`;
};

export const formatPercentage = (num?: number, decimals = 3) => {
  if (num === undefined) return "";
  return `${formatNumber(num * 100, decimals)}%`;
};
