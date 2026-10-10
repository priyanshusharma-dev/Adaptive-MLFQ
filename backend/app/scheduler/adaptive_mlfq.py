from typing import List, Dict, Any
from app.scheduler.standard_mlfq import StandardMLFQScheduler
from app.scheduler.process import Process
from app.scheduler.events import EventType
from app.ai.predictor import AdaptivePredictor

class AdaptiveMLFQScheduler(StandardMLFQScheduler):
    def __init__(self, queues, **kwargs):
        super().__init__(queues, **kwargs)
        self.adaptive_decisions: List[Dict[str, Any]] = []

    def log_adaptive_decision(self, pid: str, previous_queue: int, new_queue: int, predicted_type: str, old_quantum: int, new_quantum: int, reason: str):
        self.adaptive_decisions.append({
            "pid": pid,
            "previous_queue": previous_queue,
            "new_queue": new_queue,
            "predicted_type": predicted_type,
            "old_quantum": old_quantum,
            "new_quantum": new_quantum,
            "reason": reason,
            "time": self.time
        })

    def apply_adaptive_policy(self, process: Process) -> None:
        """Evaluates process behavior and overrides standard MLFQ demotion/promotion."""
        # Note: If the process is done or almost done, skipping AI might save overhead, but we do it anyway.
        
        old_queue = process.current_queue
        old_quantum = self.queues[old_queue].quantum or 0
        
        result = AdaptivePredictor.get_adaptive_policy(process)
        policy = result["policy"]
        predicted_type = result["prediction"]["type"].value
        
        rec_queue = policy["recommended_queue"]
        
        # Ensure queue exists
        rec_queue = min(rec_queue, len(self.queues) - 1)
        rec_queue = max(rec_queue, 0)
        
        # If AI recommends a different queue, we move it
        process.current_queue = rec_queue
        
        # In a fully dynamic system we could alter the process's individual quantum,
        # but in standard MLFQ quantums are bound to queues.
        # We can dynamically override the queue's quantum temporarily for this process,
        # or we just rely on the queue's quantum.
        # For this simulator, we'll assign an individual `current_quantum` to the process
        # if the policy recommends it, otherwise we fall back to queue's quantum.
        
        if not hasattr(process, 'dynamic_quantum'):
            process.dynamic_quantum = self.queues[process.current_queue].quantum
            
        new_quantum = policy["recommended_quantum"]
        process.dynamic_quantum = new_quantum
        
        self.queues[process.current_queue].enqueue(process)
        
        # Only log if it's an actual meaningful change
        if old_queue != process.current_queue or old_quantum != new_quantum:
            self.log_adaptive_decision(
                pid=process.pid,
                previous_queue=old_queue,
                new_queue=process.current_queue,
                predicted_type=predicted_type,
                old_quantum=old_quantum,
                new_quantum=new_quantum,
                reason=policy["reason"]
            )

    def on_io_completion(self, process: Process):
        # Instead of just returning to the same queue like Standard MLFQ, we evaluate it.
        self.apply_adaptive_policy(process)

    def handle_quantum_expiration(self):
        p = self.running_process
        self.log_gantt(p.pid, p.current_queue, self.current_slice_start, self.time, "QUANTUM_EXPIRED")
        self.log_event(EventType.QUANTUM_EXPIRED, p.pid)
        
        self.running_process = None
        
        # Switch process overhead
        p.context_switches += 1
        self.time += self.context_switch_cost
        
        # Apply AI policy on demotion instead of strictly moving down 1 level
        self.apply_adaptive_policy(p)
        
        next_proc = self.get_highest_priority_process()
        if next_proc:
            self.start_process(next_proc)

    def schedule(self):
        # We need to override schedule to use process.dynamic_quantum if it exists.
        
        for q in self.queues:
            for p in q.processes:
                p.waiting_time += 1
                if p.waiting_time > self.starvation_threshold:
                    p.starvation_status = True

        if self.running_process is None:
            next_proc = self.get_highest_priority_process()
            if next_proc:
                self.start_process(next_proc)
        else:
            if self.running_process.cpu_bursts[0] == 0:
                self.handle_burst_completion()
            else:
                # Use dynamic quantum if available, else fallback to queue quantum
                active_quantum = getattr(self.running_process, 'dynamic_quantum', self.queues[self.running_process.current_queue].quantum)
                
                if active_quantum is not None and self.time_in_current_quantum >= active_quantum:
                    self.handle_quantum_expiration()
                else:
                    if self.should_preempt(self.running_process):
                        self.handle_preemption()
                    else:
                        self.running_process.consume_cpu(1)
                        self.time_in_current_quantum += 1

    def run(self, processes):
        results = super().run(processes)
        # Append adaptive decisions to results
        results["adaptive_decisions"] = self.adaptive_decisions
        return results
