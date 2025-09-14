import { Table } from "antd";

export default function CompositionTable({ data }) {
  const columns = [
    { title: "Symbol", dataIndex: "symbol", key: "symbol" },
    { title: "Weight", dataIndex: "weight", key: "weight", render: w => (w * 100).toFixed(2) + "%" },
  ];

  return <Table dataSource={data} columns={columns} pagination={false} rowKey="symbol" />;
}
