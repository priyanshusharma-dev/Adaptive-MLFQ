import { useState, useEffect } from 'react';
import { Play, CheckCircle2, AlertCircle } from 'lucide-react';
import { runSimulation, checkHealth } from '../services/api';
import type { SimulationResponse } from '../types';
import GanttChart from '../components/GanttChart';
import QueueVisualization from '../components/QueueVisualization';

export default function Dashboard() {
  const [health, setHealth] = useState<string>('Checking...');
  const [result, setResult] = useState<SimulationResponse | null>(null);
  const [loading, setLoading] = useState(false);

  // default queues for test payload
  const defaultQueues = [
    { id: 0, quantum: 4 },
    { id: 1, quantum: 8 },
    { id: 2, quantum: 16 }
  ];

  useEffect(() => {
    checkHealth()
      .then(res => setHealth(res.status === 'ok' ? 'Connected' : 'Error'))
      .catch(() => setHealth('Disconnected'));
  }, []);

  const handleRunTest = async () => {
    setLoading(true);
    try {
      const res = await runSimulation({
        mode: 'standard',
        queues: defaultQueues,
        processes: [
          { pid: 'P1', arrival_time: 0, cpu_bursts: [12, 8], io_bursts: [5] },
          { pid: 'P2', arrival_time: 2, cpu_bursts: [4, 6], io_bursts: [10] }
        ],
        starvation_threshold: 50,
        priority_boost_interval: 100,
        context_switch_cost: 0
      });
      setResult(res);
    } catch (err) {
      console.error(err);
      alert("Failed to run simulation. Is backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <header className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Welcome to MLFQ Simulator</h1>
          <p className="text-textMuted">Design, simulate, and compare scheduling algorithms.</p>
        </div>
        
        <div className="flex items-center gap-2 card px-4 py-2">
          <div className={`w-3 h-3 rounded-full ${health === 'Connected' ? 'bg-accent' : 'bg-danger'}`} />
          <span className="text-sm font-mono">Backend: {health}</span>
        </div>
      </header>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card p-6 col-span-1 flex flex-col items-center text-center justify-center space-y-4">
          <h2 className="text-xl font-semibold">Test Connection</h2>
          <p className="text-sm text-textMuted">Run a sample workload to verify the simulation engine.</p>
          <button 
            onClick={handleRunTest}
            disabled={loading}
            className="btn-primary flex items-center gap-2 w-full justify-center"
          >
            {loading ? <AlertCircle className="animate-spin" /> : <Play size={18} />}
            {loading ? 'Simulating...' : 'Run Test Simulation'}
          </button>
        </div>
        
        {result && (
          <div className="card p-6 col-span-2 overflow-auto">
            <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <CheckCircle2 className="text-accent" />
              Simulation Results
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-background p-4 rounded-lg">
                <div className="text-textMuted text-xs mb-1">Total Time</div>
                <div className="text-xl font-mono text-primary">{result.system_metrics.total_time} ms</div>
              </div>
              <div className="bg-background p-4 rounded-lg">
                <div className="text-textMuted text-xs mb-1">Avg Turnaround</div>
                <div className="text-xl font-mono text-secondary">{result.system_metrics.avg_turnaround_time.toFixed(2)} ms</div>
              </div>
              <div className="bg-background p-4 rounded-lg">
                <div className="text-textMuted text-xs mb-1">Fairness Score</div>
                <div className="text-xl font-mono text-accent">{result.system_metrics.fairness_score}</div>
              </div>
              <div className="bg-background p-4 rounded-lg">
                <div className="text-textMuted text-xs mb-1">Context Switches</div>
                <div className="text-xl font-mono text-warning">{result.system_metrics.total_context_switches}</div>
              </div>
            </div>
          </div>
        )}
      </section>

      {result && (
        <section className="space-y-6">
          <div className="card p-6">
            <h2 className="text-xl font-semibold mb-4">Gantt Chart</h2>
            <GanttChart data={result.gantt} />
          </div>

          <QueueVisualization 
            queues={defaultQueues} 
            events={result.events} 
            maxTime={result.system_metrics.total_time} 
          />
        </section>
      )}
    </div>
  );
}
