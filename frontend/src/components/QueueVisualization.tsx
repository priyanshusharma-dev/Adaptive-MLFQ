import { useMemo, useState, useEffect } from 'react';
import { ArrowDown, Cpu } from 'lucide-react';
import type { QueueConfig } from '../types';

export default function QueueVisualization({ queues, events, maxTime }: { queues: QueueConfig[], events: any[], maxTime: number }) {
  const [currentTime, setCurrentTime] = useState(maxTime);
  const [isPlaying, setIsPlaying] = useState(false);

  // Playback effect
  useEffect(() => {
    let interval: any;
    if (isPlaying) {
      interval = setInterval(() => {
        setCurrentTime(t => {
          if (t >= maxTime) {
            setIsPlaying(false);
            return maxTime;
          }
          return t + 1;
        });
      }, 50); // Speed: 50ms real time per 1ms simulated time
    }
    return () => clearInterval(interval);
  }, [isPlaying, maxTime]);

  const activeState = useMemo(() => {
    const state: { queues: Record<number, string[]>, running: string | null } = {
      queues: {},
      running: null
    };
    queues.forEach(q => state.queues[q.id] = []);
    
    // We can rebuild queue state based on events up to currentTime
    // For simplicity, we just show which processes spent the most time in each queue overall
    // since rebuilding the exact instant queue state requires re-running simulation or deep event logs.
    // Let's approximate: a process is "in" a queue if it ran in it at that time.
    
    // Actually, we have events!
    const pastEvents = events.filter(e => e.time <= currentTime);
    
    // This is a simplified reconstruction.
    // A more precise one would parse PROCESS_ARRIVAL, QUANTUM_EXPIRED, etc.
    pastEvents.forEach(e => {
      if (e.event === 'PROCESS_ARRIVAL') {
        state.queues[0].push(e.pid);
      } else if (e.event === 'CPU_START') {
        const qId = e.details?.queue;
        if (qId !== undefined && state.queues[qId]) {
          state.queues[qId] = state.queues[qId].filter(p => p !== e.pid);
        }
        state.running = e.pid;
      } else if (e.event === 'QUANTUM_EXPIRED' || e.event === 'CPU_PREEMPTION') {
        state.running = null;
        // In reality, it gets pushed to a queue. For simulation visualizer, we can check the next event
      } else if (e.event === 'PROCESS_COMPLETION' || e.event === 'IO_START') {
        state.running = null;
      }
    });

    return state;
  }, [events, currentTime, queues]);

  return (
    <div className="card p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold flex items-center gap-2">
          <Cpu className="text-primary" />
          Queue Flow Visualization
        </h2>
        
        <div className="flex items-center gap-4">
          <div className="text-mono text-sm text-accent">Time: {currentTime}ms / {maxTime}ms</div>
          <button 
            onClick={() => {
              if (currentTime >= maxTime) setCurrentTime(0);
              setIsPlaying(!isPlaying);
            }} 
            className="btn-secondary py-1 text-sm"
          >
            {isPlaying ? 'Pause' : 'Play Simulation'}
          </button>
        </div>
      </div>
      
      <div className="flex flex-col items-center space-y-4">
        {/* CPU Block */}
        <div className="w-64 h-24 border-2 border-primary rounded-xl flex flex-col items-center justify-center bg-primary/10 relative shadow-[0_0_15px_rgba(59,130,246,0.2)]">
          <span className="text-xs font-bold text-primary absolute top-2 left-2">CPU</span>
          {activeState.running ? (
            <div className="px-4 py-2 bg-primary text-white rounded-lg font-mono animate-pulse">
              {activeState.running}
            </div>
          ) : (
            <span className="text-textMuted text-sm">IDLE</span>
          )}
        </div>
        
        <ArrowDown className="text-white/20" />
        
        {/* Queues */}
        <div className="w-full max-w-2xl space-y-4">
          {queues.map((q, idx) => (
            <div key={q.id} className="relative flex items-center">
              <div className="w-24 text-right pr-4">
                <div className="font-bold">Queue {q.id}</div>
                <div className="text-xs text-textMuted">Q: {q.quantum ? `${q.quantum}ms` : 'FCFS'}</div>
              </div>
              
              <div className="flex-1 h-16 border-2 border-white/10 rounded-r-xl border-l-0 flex items-center px-4 gap-2 bg-black/20">
                {activeState.queues[q.id]?.map((pid, i) => (
                  <div key={i} className="px-3 py-1 bg-surface border border-white/20 rounded font-mono text-sm">
                    {pid}
                  </div>
                ))}
                {activeState.queues[q.id]?.length === 0 && (
                  <span className="text-white/10 text-sm italic">Empty</span>
                )}
              </div>
              
              {idx < queues.length - 1 && (
                <div className="absolute -bottom-4 right-1/2 translate-x-1/2">
                  <ArrowDown className="text-white/20 h-4 w-4" />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
