import { useEffect, useState } from "react";
import axios from "axios";
import KPIBox from "../components/KPIBox";
import ChartCard from "../components/ChartCard";
import dayjs from "dayjs";

export default function Dashboard() {
  const [perf, setPerf] = useState([]);

  useEffect(() => {
    axios.get("http://localhost:8000/index-performance", {
      params: { start_date: "2025-05-12", end_date: "2025-09-12" }
    }).then(res => setPerf(res.data));
  }, []);

  const cumulativeOption = {
    xAxis: { type: 'category', data: perf.map(p => p.date) },
    yAxis: { type: 'value' },
    series: [{ type: 'line', data: perf.map(p => p.cumulative_return) }]
  };

  const last = perf.at(-1);
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-4 gap-4">
        <KPIBox title="Index Level" value={last?.index_level?.toFixed(2)} />
        <KPIBox title="Last Return" value={(last?.daily_return * 100).toFixed(2) + "%"} />
        <KPIBox title="Cumulative Return" value={(last?.cumulative_return * 100).toFixed(2) + "%"} />
        <KPIBox title="Days Processed" value={perf.length} />
      </div>
      <ChartCard title="Cumulative Return" option={cumulativeOption} />
    </div>
  );
}
