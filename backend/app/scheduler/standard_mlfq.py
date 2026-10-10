from typing import Optional
from app.scheduler.base_scheduler import BaseScheduler
from app.scheduler.process import Process
from app.scheduler.events import EventType

class StandardMLFQScheduler(BaseScheduler):
    def __init__(self, queues, **kwargs):
        super().__init__(queues, **kwargs)
        self.time_in_current_quantum = 0

    def on_process_arrival(self, process: Process):
        # New processes enter the highest priority queue (0)
        self.queues[0].enqueue(process)

    def on_io_completion(self, process: Process):
        # In Standard MLFQ, processes returning from I/O often retain their current queue or get a slight boost.
        # We will follow the rule: return to their current queue.
        # If we wanted to boost, we could use a different strategy.
        self.queues[process.current_queue].enqueue(process)

    def on_priority_boost(self):
        # Move all waiting processes to the highest priority queue (0)
        for i in range(1, len(self.queues)):
            processes_to_boost = self.queues[i].get_all_processes()
            for p in processes_to_boost:
                p.current_queue = 0
                self.queues[0].enqueue(p)

    def schedule(self):
        # Starvation tracking
        for q in self.queues:
            for p in q.processes:
                p.waiting_time += 1
                if p.waiting_time > self.starvation_threshold:
                    p.starvation_status = True

        if self.running_process is None:
            # Pick a new process
            next_proc = self.get_highest_priority_process()
            if next_proc:
                self.start_process(next_proc)
        else:
            # We have a running process.
            # Has it completed its current CPU burst?
            if self.running_process.cpu_bursts[0] == 0:
                self.handle_burst_completion()
            else:
                # Has it exhausted its time quantum?
                q_info = self.queues[self.running_process.current_queue]
                if q_info.quantum is not None and self.time_in_current_quantum >= q_info.quantum:
                    self.handle_quantum_expiration()
                else:
                    # Check for preemption by a higher priority queue
                    if self.should_preempt(self.running_process):
                        self.handle_preemption()
                    else:
                        # Continue running
                        self.running_process.consume_cpu(1)
                        self.time_in_current_quantum += 1
                        
                        # Note: we need to check if it JUST finished its burst in this tick
                        if self.running_process.cpu_bursts and self.running_process.cpu_bursts[0] == 0:
                            # It will be handled in the NEXT tick. But to be precise with time,
                            # actually we should handle it now if we want exact timing, or just wait for next tick.
                            pass

    def start_process(self, process: Process):
        # If it hasn't started yet, record the start time
        if process.start_time is None:
            process.start_time = self.time

        self.running_process = process
        self.current_slice_start = self.time
        self.time_in_current_quantum = 0
        
        # We need to immediately consume 1 tick for the current time unit
        process.consume_cpu(1)
        self.time_in_current_quantum += 1
        
        self.log_event(EventType.CPU_START, process.pid, {"queue": process.current_queue})

    def handle_burst_completion(self):
        p = self.running_process
        self.log_gantt(p.pid, p.current_queue, self.current_slice_start, self.time, "BURST_COMPLETED")
        
        # Pop the completed burst
        p.cpu_bursts.pop(0)
        
        if p.is_completed():
            # Process fully complete
            p.completion_time = self.time
            self.log_event(EventType.PROCESS_COMPLETION, p.pid)
        elif p.has_io():
            # Go to I/O
            io_duration = p.consume_io()
            self.io_queue.append((self.time + io_duration, p))
            self.log_event(EventType.IO_START, p.pid, {"duration": io_duration})
        else:
            # Odd case: no CPU burst left, but not completed? Should not happen if well-formed.
            # Just push back to queue.
            self.queues[p.current_queue].enqueue(p)
            
        self.running_process = None
        
        # Try to schedule immediately on this same tick
        next_proc = self.get_highest_priority_process()
        if next_proc:
            self.start_process(next_proc)

    def handle_quantum_expiration(self):
        p = self.running_process
        self.log_gantt(p.pid, p.current_queue, self.current_slice_start, self.time, "QUANTUM_EXPIRED")
        self.log_event(EventType.QUANTUM_EXPIRED, p.pid)
        
        # Demote if possible
        next_queue_id = min(p.current_queue + 1, len(self.queues) - 1)
        p.current_queue = next_queue_id
        
        self.queues[next_queue_id].enqueue(p)
        self.running_process = None
        
        # Switch process
        p.context_switches += 1
        self.time += self.context_switch_cost # Note: context switch cost is added here
        
        next_proc = self.get_highest_priority_process()
        if next_proc:
            self.start_process(next_proc)

    def handle_preemption(self):
        p = self.running_process
        self.log_gantt(p.pid, p.current_queue, self.current_slice_start, self.time, "PREEMPTED")
        self.log_event(EventType.CPU_PREEMPTION, p.pid)
        
        p.preemptions += 1
        
        # Return to same queue
        self.queues[p.current_queue].enqueue(p)
        self.running_process = None
        
        p.context_switches += 1
        self.time += self.context_switch_cost
        
        next_proc = self.get_highest_priority_process()
        if next_proc:
            self.start_process(next_proc)

    def should_preempt(self, process: Process) -> bool:
        # Check if there is a process in a strictly higher priority queue
        for i in range(process.current_queue):
            if not self.queues[i].is_empty():
                return True
        return False
