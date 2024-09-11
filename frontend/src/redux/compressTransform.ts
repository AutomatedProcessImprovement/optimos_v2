import { createTransform } from "redux-persist";
import LZ from "lz-string";
import stringify from "json-stringify-safe";

export const compressTransform = createTransform(
  (state) => LZ.compressToUTF16(stringify(state)),
  (state) => {
    if (typeof state !== "string") {
      return state;
    }
    try {
      return JSON.parse(LZ.decompressFromUTF16(state));
    } catch (err) {
      return null;
    }
  }
);
