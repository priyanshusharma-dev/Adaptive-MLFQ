from typing import List, Optional
from app.scheduler.process import Process

class Queue:
    def __init__(self, queue_id: int, priority: int, quantum: Optional[int] = None):
        """
        queue_id: ID of the queue (0 is highest priority usually).
        priority: Lower number means higher priority.
        quantum: Time quantum in milliseconds. If None, it's FCFS.
        """
        self.queue_id = queue_id
        self.priority = priority
        self.quantum = quantum
        self.processes: List[Process] = []

    def enqueue(self, process: Process):
        """Adds a process to the end of the queue."""
        process.current_queue = self.queue_id
        self.processes.append(process)

    def dequeue(self) -> Optional[Process]:
        """Removes and returns the first process in the queue."""
        if self.is_empty():
            return None
        return self.processes.pop(0)

    def is_empty(self) -> bool:
        return len(self.processes) == 0

    def size(self) -> int:
        return len(self.processes)
        
    def remove_process(self, pid: str) -> Optional[Process]:
        """Removes a specific process by PID, used for things like priority boosting."""
        for i, p in enumerate(self.processes):
            if p.pid == pid:
                return self.processes.pop(i)
        return None

    def get_all_processes(self) -> List[Process]:
        """Returns and clears all processes. Useful for priority boosting."""
        procs = self.processes
        self.processes = []
        return procs
