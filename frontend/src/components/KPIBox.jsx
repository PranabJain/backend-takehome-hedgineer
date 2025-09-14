export default function KPIBox({ title, value, subtitle }) {
  return (
    <div className="bg-white rounded shadow px-4 py-3 text-center">
      <h4 className="text-gray-500 text-sm">{title}</h4>
      <p className="text-2xl font-bold">{value}</p>
      {subtitle && <p className="text-gray-400 text-xs">{subtitle}</p>}
    </div>
  );
}
