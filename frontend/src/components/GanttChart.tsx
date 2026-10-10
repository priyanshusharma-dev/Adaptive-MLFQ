import { useMemo } from 'react';
import type { GanttSegment } from '../types';

export default function GanttChart({ data }: { data: GanttSegment[] }) {
  const maxTime = useMemo(() => {
    if (!data || data.length === 0) return 0;
    return Math.max(...data.map(d => d.end));
  }, [data]);

  const uniquePids = useMemo(() => {
    if (!data) return [];
    return Array.from(new Set(data.map(d => d.pid))).sort();
  }, [data]);

  const colors = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6'];

  if (!data || data.length === 0) {
    return <div className="text-center p-8 text-textMuted">No simulation data available</div>;
  }

  return (
    <div className="w-full overflow-x-auto pb-8 pt-28 -mt-24">
      <div className="min-w-[800px] relative mt-24 z-10">
        {uniquePids.map((pid, idx) => {
          const processSegments = data.filter(d => d.pid === pid);
          const color = colors[idx % colors.length];

          return (
            <div key={pid} className="flex items-center mb-6 relative h-10">
              <div className="w-16 flex-shrink-0 font-mono font-bold text-sm text-textMuted">{pid}</div>
              <div className="flex-1 relative h-full bg-surface border-y border-white/5">
                {processSegments.map((seg, i) => {
                  const left = (seg.start / maxTime) * 100;
                  const width = ((seg.end - seg.start) / maxTime) * 100;
                  
                  return (
                    <div
                      key={i}
                      className="absolute top-1 bottom-1 rounded-sm cursor-pointer hover:opacity-80 transition-opacity group"
                      style={{
                        left: `${left}%`,
                        width: `${width}%`,
                        backgroundColor: color,
                      }}
                    >
                      <div className="absolute hidden group-hover:block bottom-full left-1/2 -translate-x-1/2 mb-2 p-2 bg-black text-xs text-white rounded whitespace-nowrap z-50 shadow-lg border border-white/20">
                        PID: {seg.pid} <br/>
                        Queue: {seg.queue} <br/>
                        Time: {seg.start}ms - {seg.end}ms <br/>
                        Event: {seg.event}
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
        
        {/* Timeline Axis */}
        <div className="flex ml-16 border-t border-white/20 pt-2 text-xs text-textMuted">
          {[0, 0.25, 0.5, 0.75, 1].map((pct, i) => (
            <div key={i} className="absolute" style={{ left: `calc(4rem + ${pct * 100}%)`, transform: 'translateX(-50%)' }}>
              {Math.round(maxTime * pct)}ms
              <div className="absolute top-[-10px] left-1/2 w-px h-2 bg-white/20 -translate-x-1/2" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
