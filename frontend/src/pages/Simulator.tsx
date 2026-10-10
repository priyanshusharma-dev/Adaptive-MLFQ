import { useState } from 'react';
import { runSimulation, generateWorkload } from '../services/api';
import type { SimulationResponse, ProcessConfig } from '../types';
import GanttChart from '../components/GanttChart';
import QueueVisualization from '../components/QueueVisualization';
import AdaptiveDecisionsPanel from '../components/AdaptiveDecisionsPanel';
import { Play, FileCode, RefreshCw } from 'lucide-react';

export default function Simulator() {
  const [workloadType, setWorkloadType] = useState('mixed');
  const [processCount, setProcessCount] = useState(5);
  const [seed, setSeed] = useState(42);
  const [processes, setProcesses] = useState<ProcessConfig[]>([]);
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SimulationResponse | null>(null);

  const defaultQueues = [
    { id: 0, quantum: 4 },
    { id: 1, quantum: 8 },
    { id: 2, quantum: 16 }
  ];

  const handleGenerate = async () => {
    try {
      const generated = await generateWorkload(workloadType, processCount, seed);
      setProcesses(generated);
      setResult(null); // clear previous run
    } catch (err) {
      console.error(err);
      alert('Failed to generate workload');
    }
  };

  const handleRun = async (mode: 'standard' | 'adaptive') => {
    if (processes.length === 0) return alert('Generate a workload first.');
    setLoading(true);
    try {
      const res = await runSimulation({
        mode,
        queues: defaultQueues,
        processes,
        starvation_threshold: 50,
        priority_boost_interval: 100,
        context_switch_cost: 1
      });
      setResult(res);
    } catch (err) {
      console.error(err);
      alert('Failed to run simulation');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <header>
        <h1 className="text-3xl font-bold text-white mb-2">Simulator & Workloads</h1>
        <p className="text-textMuted">Generate process workloads and run Phase 1 experiments.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="card p-6 space-y-6">
          <h2 className="text-xl font-semibold flex items-center gap-2">
            <FileCode className="text-primary" />
            Workload Config
          </h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-textMuted mb-1">Workload Type</label>
              <select 
                value={workloadType} 
                onChange={e => setWorkloadType(e.target.value)}
                className="w-full bg-background border border-white/10 rounded-lg p-2 text-white"
              >
                <option value="mixed">Mixed</option>
                <option value="cpu_heavy">CPU Heavy</option>
                <option value="io_heavy">I/O Heavy</option>
                <option value="interactive">Interactive</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm text-textMuted mb-1">Process Count</label>
              <input 
                type="number" 
                value={processCount} 
                onChange={e => setProcessCount(Number(e.target.value))}
                className="w-full bg-background border border-white/10 rounded-lg p-2 text-white"
              />
            </div>

            <div>
              <label className="block text-sm text-textMuted mb-1">Random Seed</label>
              <input 
                type="number" 
                value={seed} 
                onChange={e => setSeed(Number(e.target.value))}
                className="w-full bg-background border border-white/10 rounded-lg p-2 text-white"
              />
            </div>
            
            <button onClick={handleGenerate} className="btn-secondary w-full flex justify-center items-center gap-2">
              <RefreshCw size={18} />
              Generate Processes
            </button>
          </div>
        </div>

        {/* Process List Preview */}
        <div className="card p-6 col-span-2 flex flex-col h-96">
          <h2 className="text-xl font-semibold mb-4">Generated Processes ({processes.length})</h2>
          <div className="flex-1 overflow-auto bg-background rounded-lg border border-white/10 p-2">
            {processes.length === 0 ? (
              <div className="h-full flex items-center justify-center text-textMuted">
                No processes generated yet.
              </div>
            ) : (
              <table className="w-full text-left text-sm">
                <thead className="sticky top-0 bg-background text-textMuted p-2">
                  <tr>
                    <th className="p-2 border-b border-white/10">PID</th>
                    <th className="p-2 border-b border-white/10">Arrival</th>
                    <th className="p-2 border-b border-white/10">CPU Bursts</th>
                    <th className="p-2 border-b border-white/10">I/O Bursts</th>
                  </tr>
                </thead>
                <tbody>
                  {processes.map(p => (
                    <tr key={p.pid} className="hover:bg-white/5 border-b border-white/5">
                      <td className="p-2 font-mono text-primary">{p.pid}</td>
                      <td className="p-2">{p.arrival_time}</td>
                      <td className="p-2 font-mono text-xs">{JSON.stringify(p.cpu_bursts)}</td>
                      <td className="p-2 font-mono text-xs text-secondary">{JSON.stringify(p.io_bursts)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
          
          <div className="flex flex-col gap-2 mt-4">
            <button 
              onClick={() => handleRun('standard')}
              disabled={processes.length === 0 || loading}
              className="btn-secondary flex justify-center items-center gap-2"
            >
              {loading ? <RefreshCw className="animate-spin" /> : <Play size={18} />}
              Run Standard MLFQ
            </button>
            <button 
              onClick={() => handleRun('adaptive')}
              disabled={processes.length === 0 || loading}
              className="btn-primary flex justify-center items-center gap-2"
            >
              {loading ? <RefreshCw className="animate-spin" /> : <Play size={18} />}
              Run Adaptive MLFQ (Phase 2)
            </button>
          </div>
        </div>
      </div>

      {result && (
        <section className="space-y-6 mt-8 animate-in fade-in slide-in-from-bottom-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-surface border border-white/10 p-4 rounded-xl shadow-lg">
                <div className="text-textMuted text-xs mb-1">Total Time</div>
                <div className="text-xl font-mono text-primary">{result.system_metrics.total_time} ms</div>
              </div>
              <div className="bg-surface border border-white/10 p-4 rounded-xl shadow-lg">
                <div className="text-textMuted text-xs mb-1">Avg Turnaround</div>
                <div className="text-xl font-mono text-secondary">{result.system_metrics.avg_turnaround_time.toFixed(2)} ms</div>
              </div>
              <div className="bg-surface border border-white/10 p-4 rounded-xl shadow-lg">
                <div className="text-textMuted text-xs mb-1">Fairness Score</div>
                <div className="text-xl font-mono text-accent">{result.system_metrics.fairness_score}</div>
              </div>
              <div className="bg-surface border border-white/10 p-4 rounded-xl shadow-lg">
                <div className="text-textMuted text-xs mb-1">Context Switches</div>
                <div className="text-xl font-mono text-warning">{result.system_metrics.total_context_switches}</div>
              </div>
            </div>

          <div className="card p-6">
            <h2 className="text-xl font-semibold mb-4">Gantt Chart</h2>
            <GanttChart data={result.gantt} />
          </div>

          <QueueVisualization 
            queues={defaultQueues} 
            events={result.events} 
            maxTime={result.system_metrics.total_time} 
          />

          {result.adaptive_decisions && result.adaptive_decisions.length > 0 && (
            <AdaptiveDecisionsPanel decisions={result.adaptive_decisions} />
          )}
        </section>
      )}
    </div>
  );
}
