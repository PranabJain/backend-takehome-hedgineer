import { useEffect, useState } from "react";
import ChartCard from "../components/ChartCard";
import axios from "axios";

export default function Performance() {
  const [perf, setPerf] = useState([]);

  useEffect(() => {
    axios.get("http://localhost:8000/index-performance", {
      params: { start_date: "2025-05-12", end_date: "2025-09-12" }
    }).then(res => setPerf(res.data));
  }, []);

  return (
    <div className="space-y-4">
      <ChartCard
        title="Daily Return"
        option={{
          xAxis: { type: 'category', data: perf.map(p => p.date) },
          yAxis: { type: 'value' },
          series: [{ type: 'bar', data: perf.map(p => p.daily_return) }]
        }}
      />
    </div>
  );
}
