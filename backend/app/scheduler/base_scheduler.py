from typing import List, Dict, Optional, Tuple
from app.scheduler.process import Process
from app.scheduler.queue import Queue
from app.scheduler.events import Event, EventType

class BaseScheduler:
    def __init__(self, queues: List[Queue], starvation_threshold: int = 50, priority_boost_interval: int = 100, context_switch_cost: int = 0):
        self.queues = queues
        self.starvation_threshold = starvation_threshold
        self.priority_boost_interval = priority_boost_interval
        self.context_switch_cost = context_switch_cost
        
        self.time = 0
        self.events: List[Event] = []
        self.gantt: List[Dict] = []
        
        self.processes: Dict[str, Process] = {}
        self.io_queue: List[Tuple[int, Process]] = [] # list of (io_completion_time, process)
        self.running_process: Optional[Process] = None
        self.current_slice_start: int = 0
        
        self.last_boost_time: int = 0
        
    def log_event(self, event_type: EventType, pid: Optional[str] = None, details: Optional[Dict] = None):
        self.events.append(Event(self.time, event_type, pid, details))
        
    def log_gantt(self, pid: str, queue_id: int, start: int, end: int, event_type: str):
        if start < end:
            self.gantt.append({
                "pid": pid,
                "queue": queue_id,
                "start": start,
                "end": end,
                "event": event_type
            })

    def run(self, processes: List[Process]):
        # Reset state
        self.time = 0
        self.events = []
        self.gantt = []
        self.io_queue = []
        self.running_process = None
        self.processes = {p.pid: p for p in processes}
        self.last_boost_time = 0
        
        # Ensure queues are empty initially
        for q in self.queues:
            q.processes = []

        unarrived_processes = sorted(processes, key=lambda p: p.arrival_time)
        
        # Main simulation loop
        while unarrived_processes or not self.all_queues_empty() or self.io_queue or self.running_process:
            self.handle_arrivals(unarrived_processes)
            self.handle_io_completions()
            self.handle_priority_boost()
            
            self.schedule()
            
            self.time += 1
            
        # Compute final metrics for all processes
        for p in self.processes.values():
            p.calculate_metrics()
            
        return {
            "gantt": self.gantt,
            "events": [e.to_dict() for e in self.events],
            "processes": [p.to_dict() for p in self.processes.values()]
        }

    def all_queues_empty(self) -> bool:
        return all(q.is_empty() for q in self.queues)

    def handle_arrivals(self, unarrived_processes: List[Process]):
        while unarrived_processes and unarrived_processes[0].arrival_time == self.time:
            p = unarrived_processes.pop(0)
            self.log_event(EventType.PROCESS_ARRIVAL, p.pid)
            self.on_process_arrival(p)

    def handle_io_completions(self):
        # I/O completion logic
        completed_io = [item for item in self.io_queue if item[0] == self.time]
        self.io_queue = [item for item in self.io_queue if item[0] > self.time]
        
        for _, p in completed_io:
            self.log_event(EventType.IO_COMPLETE, p.pid)
            self.on_io_completion(p)

    def handle_priority_boost(self):
        if self.priority_boost_interval > 0 and self.time > 0 and self.time - self.last_boost_time >= self.priority_boost_interval:
            self.log_event(EventType.PRIORITY_BOOST)
            self.on_priority_boost()
            self.last_boost_time = self.time

    def get_highest_priority_process(self) -> Optional[Process]:
        for q in self.queues:
            if not q.is_empty():
                return q.dequeue()
        return None

    # Abstract methods to be implemented by specific schedulers
    def on_process_arrival(self, process: Process):
        raise NotImplementedError
        
    def on_io_completion(self, process: Process):
        raise NotImplementedError
        
    def on_priority_boost(self):
        raise NotImplementedError
        
    def schedule(self):
        raise NotImplementedError
