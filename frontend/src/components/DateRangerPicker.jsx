import { DatePicker } from "antd";
const { RangePicker } = DatePicker;

export default function DateRangePicker({ onChange, defaultValue }) {
  return (
    <RangePicker
      defaultValue={defaultValue}
      format="YYYY-MM-DD"
      onChange={onChange}
    />
  );
}
