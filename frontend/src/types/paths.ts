type Join<K, P> = K extends string
  ? P extends string
    ? `${K}${"" extends P ? "" : "."}${P}`
    : never
  : never;

export type Paths<T> = T extends object
  ? {
      [K in keyof T]-?: K extends string
        ? `${K}` | Join<K, Paths<T[K]>>
        : never;
    }[keyof T]
  : "";

export type Leaves<T> = T extends object
  ? {
      [K in keyof T]-?: Join<K, Leaves<T[K]>>;
    }[keyof T]
  : "";
