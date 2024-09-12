import { Select, SelectProps } from "@mantine/core";
import React, { useMemo } from "react";
import { FC } from "react";

interface NumberSelectProps
  extends Omit<SelectProps, "value" | "onChange" | "data"> {
  value: number;
  onChange: (value: number) => void;
  data: Array<{ value: number; label: string; disabled?: boolean }>;
}

const NumberSelect: FC<NumberSelectProps> = (props) => {
  const { value, onChange, ...otherProps } = props;
  const data = useMemo(() => {
    return props.data.map((it) => ({ ...it, value: it.value.toString() }));
  }, [props.data]);
  return (
    <Select
      {...otherProps}
      value={value.toString()}
      onChange={(it) => onChange(Number(it) || 0)}
      data={data}
    />
  );
};

export default NumberSelect;
