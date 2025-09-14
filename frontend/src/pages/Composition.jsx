import { useEffect, useState } from "react";
import CompositionTable from "../components/CompositionTable";
import axios from "axios";

export default function Composition() {
  const [data, setData] = useState([]);

  useEffect(() => {
    axios.get("http://localhost:8000/index-composition", {
      params: { date: "2025-09-12" }
    }).then(res => setData(res.data));
  }, []);

  return (
    <div className="bg-white rounded shadow p-4">
      <h3 className="font-semibold mb-3">Index Composition</h3>
      <CompositionTable data={data} />
    </div>
  );
}
