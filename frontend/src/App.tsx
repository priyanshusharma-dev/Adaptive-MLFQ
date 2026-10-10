import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Activity, LayoutDashboard, Settings, GitCompare, Home } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Simulator from './pages/Simulator';
import Compare from './pages/Compare';
import InkOrbitHero from './components/InkOrbitHero';

function Sidebar() {
  return (
    <div className="w-64 bg-surface h-screen border-r border-white/10 flex flex-col">
      <div className="p-6">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <Activity className="text-primary" />
          Adaptive MLFQ
        </h1>
      </div>
      <nav className="flex-1 px-4 space-y-2">
        <Link to="/" className="flex items-center gap-3 px-4 py-3 text-textMuted hover:text-white hover:bg-white/5 rounded-lg transition-colors">
          <Home size={20} />
          Home
        </Link>
        <Link to="/dashboard" className="flex items-center gap-3 px-4 py-3 text-textMuted hover:text-white hover:bg-white/5 rounded-lg transition-colors">
          <LayoutDashboard size={20} />
          Dashboard
        </Link>
        <Link to="/simulator" className="flex items-center gap-3 px-4 py-3 text-textMuted hover:text-white hover:bg-white/5 rounded-lg transition-colors">
          <Settings size={20} />
          Simulator
        </Link>
        <Link to="/compare" className="flex items-center gap-3 px-4 py-3 text-textMuted hover:text-white hover:bg-white/5 rounded-lg transition-colors">
          <GitCompare size={20} />
          Compare Phases
        </Link>
      </nav>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="flex h-screen overflow-hidden bg-background">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<InkOrbitHero theme="dark" />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/simulator" element={<Simulator />} />
            <Route path="/compare" element={<Compare />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
