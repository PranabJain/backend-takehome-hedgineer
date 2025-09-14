import axios from "axios";
import { Button, DatePicker, message } from "antd";
import { useState } from "react";

const { RangePicker } = DatePicker;

export default function ExportData() {
  const [dates, setDates] = useState([]);
  
  const handleExport = () => {
    if (!dates.length) return;
    axios.post("http://localhost:8000/export-data", {
      start_date: dates[0].format("YYYY-MM-DD"),
      end_date: dates[1].format("YYYY-MM-DD")
    }, { responseType: 'blob' }).then(res => {
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "index_export.xlsx");
      document.body.appendChild(link);
      link.click();
      message.success("Export downloaded");
    });
  };

  return (
    <div className="space-y-4">
      <RangePicker onChange={(vals) => setDates(vals)} />
      <Button type="primary" onClick={handleExport}>Export Excel</Button>
    </div>
  );
}
