import { useState } from 'react';
import { runSimulation, generateWorkload } from '../services/api';
import type { SimulationResponse, ProcessConfig } from '../types';
import { GitCompare, Play, RefreshCw, Download } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

export default function Compare() {
  const [workloadType, setWorkloadType] = useState('mixed');
  const [processCount, setProcessCount] = useState(10);
  const [seed, setSeed] = useState(42);
  const [processes, setProcesses] = useState<ProcessConfig[]>([]);
  
  const [loading, setLoading] = useState(false);
  const [stdResult, setStdResult] = useState<SimulationResponse | null>(null);
  const [adapResult, setAdapResult] = useState<SimulationResponse | null>(null);

  const defaultQueues = [
    { id: 0, quantum: 4 },
    { id: 1, quantum: 8 },
    { id: 2, quantum: 16 }
  ];

  const handleGenerate = async () => {
    try {
      const generated = await generateWorkload(workloadType, processCount, seed);
      setProcesses(generated);
      setStdResult(null);
      setAdapResult(null);
    } catch (err) {
      console.error(err);
      alert('Failed to generate workload');
    }
  };

  const handleRunComparison = async () => {
    if (processes.length === 0) return alert('Generate a workload first.');
    setLoading(true);
    try {
      const pStd = runSimulation({
        mode: 'standard',
        queues: defaultQueues,
        processes,
        starvation_threshold: 50,
        priority_boost_interval: 100,
        context_switch_cost: 1
      });

      const pAdap = runSimulation({
        mode: 'adaptive',
        queues: defaultQueues,
        processes,
        starvation_threshold: 50,
        priority_boost_interval: 100,
        context_switch_cost: 1
      });

      const [resStd, resAdap] = await Promise.all([pStd, pAdap]);
      setStdResult(resStd);
      setAdapResult(resAdap);
    } catch (err) {
      console.error(err);
      alert('Failed to run comparison simulations');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = (format: 'json' | 'csv') => {
    if (!stdResult || !adapResult) return;
    
    if (format === 'json') {
      const payload = JSON.stringify({ standard: stdResult, adaptive: adapResult }, null, 2);
      const blob = new Blob([payload], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `experiment_results_${seed}.json`;
      a.click();
    } else {
      const headers = ['Metric', 'Standard MLFQ', 'Adaptive MLFQ'];
      const rows = [
        ['Total Time (ms)', stdResult.system_metrics.total_time, adapResult.system_metrics.total_time],
        ['Avg Turnaround', stdResult.system_metrics.avg_turnaround_time.toFixed(2), adapResult.system_metrics.avg_turnaround_time.toFixed(2)],
        ['Avg Waiting', stdResult.system_metrics.avg_waiting_time.toFixed(2), adapResult.system_metrics.avg_waiting_time.toFixed(2)],
        ['Context Switches', stdResult.system_metrics.total_context_switches, adapResult.system_metrics.total_context_switches],
        ['Fairness Score', stdResult.system_metrics.fairness_score, adapResult.system_metrics.fairness_score],
        ['Starved Processes', stdResult.system_metrics.starved_processes_count, adapResult.system_metrics.starved_processes_count],
      ];
      const csvContent = [headers.join(',')]
        .concat(rows.map(e => e.join(',')))
        .join('\n');
      
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `experiment_results_${seed}.csv`;
      a.click();
    }
  };

  const renderComparisonChart = () => {
    if (!stdResult || !adapResult) return null;

    const data = [
      {
        name: 'Total Time',
        Standard: stdResult.system_metrics.total_time,
        Adaptive: adapResult.system_metrics.total_time,
      },
      {
        name: 'Avg Turnaround',
        Standard: stdResult.system_metrics.avg_turnaround_time,
        Adaptive: adapResult.system_metrics.avg_turnaround_time,
      },
      {
        name: 'Avg Waiting',
        Standard: stdResult.system_metrics.avg_waiting_time,
        Adaptive: adapResult.system_metrics.avg_waiting_time,
      },
      {
        name: 'Context Switches',
        Standard: stdResult.system_metrics.total_context_switches,
        Adaptive: adapResult.system_metrics.total_context_switches,
      }
    ];

    return (
      <div className="h-80 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="name" stroke="#94A3B8" />
            <YAxis stroke="#94A3B8" />
            <Tooltip contentStyle={{ backgroundColor: '#1E293B', borderColor: '#334155', color: '#F8FAFC' }} />
            <Legend />
            <Bar dataKey="Standard" fill="#94A3B8" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Adaptive" fill="#3B82F6" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    );
  };

  return (
    <div className="p-8 max-w-7xl mx-auto space-y-8">
      <header>
        <h1 className="text-3xl font-bold text-white mb-2">Phase Comparison Dashboard</h1>
        <p className="text-textMuted">Compare Standard MLFQ vs Adaptive MLFQ on identical workloads side-by-side.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card p-6 col-span-1 space-y-4">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <GitCompare className="text-primary" /> Setup
          </h2>
          <div>
            <label className="block text-sm text-textMuted mb-1">Workload</label>
            <select 
              value={workloadType} 
              onChange={e => setWorkloadType(e.target.value)}
              className="w-full bg-background border border-white/10 rounded-lg p-2 text-white text-sm"
            >
              <option value="mixed">Mixed</option>
              <option value="cpu_heavy">CPU Heavy</option>
              <option value="io_heavy">I/O Heavy</option>
              <option value="interactive">Interactive</option>
            </select>
          </div>
          <div>
            <label className="block text-sm text-textMuted mb-1">Count</label>
            <input type="number" value={processCount} onChange={e => setProcessCount(Number(e.target.value))} className="w-full bg-background border border-white/10 rounded-lg p-2 text-white text-sm" />
          </div>
          <div>
            <label className="block text-sm text-textMuted mb-1">Seed</label>
            <input type="number" value={seed} onChange={e => setSeed(Number(e.target.value))} className="w-full bg-background border border-white/10 rounded-lg p-2 text-white text-sm" />
          </div>
          <button onClick={handleGenerate} className="btn-secondary w-full text-sm">Generate</button>
          
          <div className="pt-4 border-t border-white/10">
            <button onClick={handleRunComparison} disabled={processes.length === 0 || loading} className="btn-primary w-full text-sm flex justify-center items-center gap-2">
              {loading ? <RefreshCw className="animate-spin" size={16} /> : <Play size={16} />}
              Run Comparison
            </button>
          </div>
          <div className="text-xs text-textMuted text-center mt-2">
            {processes.length > 0 ? `${processes.length} processes ready` : 'No processes loaded'}
          </div>
        </div>

        <div className="col-span-3 space-y-6">
          {stdResult && adapResult ? (
            <>
              <div className="flex justify-end gap-2 mb-2">
                <button onClick={() => handleExport('csv')} className="btn-secondary py-1 text-sm flex items-center gap-2">
                  <Download size={14} /> Export CSV
                </button>
                <button onClick={() => handleExport('json')} className="btn-secondary py-1 text-sm flex items-center gap-2">
                  <Download size={14} /> Export JSON
                </button>
              </div>

              <div className="card p-6">
                <h2 className="text-lg font-semibold mb-4">Performance Comparison</h2>
                {renderComparisonChart()}
              </div>
              
              <div className="grid grid-cols-2 gap-6">
                <div className="card p-6 border-t-4 border-t-textMuted">
                  <h3 className="text-lg font-bold mb-4">Standard MLFQ</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between border-b border-white/5 pb-2">
                      <span className="text-textMuted">Total Time</span>
                      <span className="font-mono">{stdResult.system_metrics.total_time}</span>
                    </div>
                    <div className="flex justify-between border-b border-white/5 pb-2">
                      <span className="text-textMuted">Avg Turnaround</span>
                      <span className="font-mono">{stdResult.system_metrics.avg_turnaround_time.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between border-b border-white/5 pb-2">
                      <span className="text-textMuted">Fairness Score</span>
                      <span className="font-mono text-accent">{stdResult.system_metrics.fairness_score}</span>
                    </div>
                    <div className="flex justify-between border-b border-white/5 pb-2">
                      <span className="text-textMuted">Starved Count</span>
                      <span className="font-mono text-danger">{stdResult.system_metrics.starved_processes_count}</span>
                    </div>
                  </div>
                </div>

                <div className="card p-6 border-t-4 border-t-primary">
                  <h3 className="text-lg font-bold mb-4 text-primary">Adaptive MLFQ</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between border-b border-white/5 pb-2">
                      <span className="text-textMuted">Total Time</span>
                      <span className="font-mono">{adapResult.system_metrics.total_time}</span>
                    </div>
                    <div className="flex justify-between border-b border-white/5 pb-2">
                      <span className="text-textMuted">Avg Turnaround</span>
                      <span className="font-mono">{adapResult.system_metrics.avg_turnaround_time.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between border-b border-white/5 pb-2">
                      <span className="text-textMuted">Fairness Score</span>
                      <span className="font-mono text-accent">{adapResult.system_metrics.fairness_score}</span>
                    </div>
                    <div className="flex justify-between border-b border-white/5 pb-2">
                      <span className="text-textMuted">Starved Count</span>
                      <span className="font-mono text-danger">{adapResult.system_metrics.starved_processes_count}</span>
                    </div>
                  </div>
                </div>
              </div>
            </>
          ) : (
            <div className="card p-6 h-full flex flex-col items-center justify-center text-textMuted">
              <GitCompare size={48} className="mb-4 opacity-50" />
              <p>Configure and run the comparison to see metrics.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
