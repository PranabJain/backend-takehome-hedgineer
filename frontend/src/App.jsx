import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Performance from "./pages/Performance";
import Composition from "./pages/Composition";
import Changes from "./pages/Changes";
import ExportData from "./pages/ExportData";

export default function App() {
  return (
    <Router>
      <div className="bg-white shadow p-4 flex gap-6">
        <Link to="/">Dashboard</Link>
        <Link to="/performance">Performance</Link>
        <Link to="/composition">Composition</Link>
        <Link to="/changes">Changes</Link>
        <Link to="/export">Export</Link>
      </div>
      <div className="p-6">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/performance" element={<Performance />} />
          <Route path="/composition" element={<Composition />} />
          <Route path="/changes" element={<Changes />} />
          <Route path="/export" element={<ExportData />} />
        </Routes>
      </div>
    </Router>
  );
}
