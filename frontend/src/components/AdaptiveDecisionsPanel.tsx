import { BrainCircuit, ArrowRight } from 'lucide-react';

export default function AdaptiveDecisionsPanel({ decisions }: { decisions: any[] }) {
  if (!decisions || decisions.length === 0) {
    return null;
  }

  return (
    <div className="card p-6">
      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <BrainCircuit className="text-accent" />
        AI Adaptive Decisions
      </h2>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-black/20 text-textMuted border-b border-white/10">
            <tr>
              <th className="p-3">Time</th>
              <th className="p-3">PID</th>
              <th className="p-3">Classification</th>
              <th className="p-3">Queue Adjustment</th>
              <th className="p-3">Quantum Change</th>
              <th className="p-3">Reason</th>
            </tr>
          </thead>
          <tbody>
            {decisions.map((d, i) => (
              <tr key={i} className="border-b border-white/5 hover:bg-white/5">
                <td className="p-3 text-textMuted">{d.time}ms</td>
                <td className="p-3 font-mono font-bold text-primary">{d.pid}</td>
                <td className="p-3">
                  <span className={`px-2 py-1 rounded text-xs ${d.predicted_type === 'CPU_BOUND' ? 'bg-danger/20 text-danger' : d.predicted_type === 'IO_BOUND' ? 'bg-primary/20 text-primary' : 'bg-warning/20 text-warning'}`}>
                    {d.predicted_type}
                  </span>
                </td>
                <td className="p-3 flex items-center gap-2">
                  Q{d.previous_queue} <ArrowRight size={14} className="text-textMuted" /> Q{d.new_queue ?? 'X'}
                </td>
                <td className="p-3">
                  {d.old_quantum}ms <ArrowRight size={14} className="inline text-textMuted mx-1" /> {d.new_quantum}ms
                </td>
                <td className="p-3 text-textMuted italic">{d.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
