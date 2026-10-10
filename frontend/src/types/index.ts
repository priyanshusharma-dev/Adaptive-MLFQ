export interface ProcessConfig {
  pid: string;
  arrival_time: number;
  cpu_bursts: number[];
  io_bursts: number[];
}

export interface QueueConfig {
  id: number;
  quantum: number | null;
}

export interface SimulationRequest {
  mode: string;
  queues: QueueConfig[];
  processes: ProcessConfig[];
  starvation_threshold: number;
  priority_boost_interval: number;
  context_switch_cost: number;
}

export interface GanttSegment {
  pid: string;
  queue: number;
  start: number;
  end: number;
  event: string;
}

export interface SimulationResponse {
  simulation_id: string;
  gantt: GanttSegment[];
  process_metrics: any[];
  system_metrics: {
    avg_waiting_time: number;
    avg_response_time: number;
    avg_turnaround_time: number;
    throughput: number;
    total_context_switches: number;
    fairness_score: number;
    starved_processes_count: number;
    total_time: number;
  };
  events: any[];
  adaptive_decisions?: any[];
}
