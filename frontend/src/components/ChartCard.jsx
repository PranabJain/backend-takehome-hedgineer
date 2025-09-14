import ReactECharts from 'echarts-for-react';

export default function ChartCard({ title, option }) {
  return (
    <div className="bg-white rounded shadow p-4">
      <h3 className="font-semibold mb-3">{title}</h3>
      <ReactECharts option={option} style={{ height: 300 }} />
    </div>
  );
}
