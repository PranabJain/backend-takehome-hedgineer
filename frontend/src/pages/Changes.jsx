import { useEffect, useState } from "react";
import axios from "axios";
import { Table, Tag } from "antd";

export default function Changes() {
  const [changes, setChanges] = useState([]);

  useEffect(() => {
    axios.get("http://localhost:8000/composition-changes", {
      params: { start_date: "2025-05-12", end_date: "2025-09-12" }
    }).then(res => setChanges(res.data));
  }, []);

  const columns = [
    { title: "Date", dataIndex: "date", key: "date" },
    { title: "Entered", dataIndex: "entered", render: entered => entered.map(sym => <Tag color="green">{sym}</Tag>) },
    { title: "Exited", dataIndex: "exited", render: exited => exited.map(sym => <Tag color="red">{sym}</Tag>) }
  ];

  return <Table dataSource={changes} columns={columns} rowKey="date" />;
}
