from typing import List, Optional
from enum import Enum

class ProcessType(str, Enum):
    CPU_BOUND = "CPU_BOUND"
    IO_BOUND = "IO_BOUND"
    INTERACTIVE = "INTERACTIVE"
    MIXED = "MIXED"
    UNKNOWN = "UNKNOWN"

class Process:
    def __init__(
        self,
        pid: str,
        arrival_time: int,
        cpu_bursts: List[int],
        io_bursts: List[int],
        priority: int = 0,
        process_type: ProcessType = ProcessType.UNKNOWN,
    ):
        self.pid = pid
        self.arrival_time = arrival_time
        
        # Original configuration for tracking and reproducibility
        self.original_cpu_bursts = list(cpu_bursts)
        self.original_io_bursts = list(io_bursts)
        
        # Current state
        self.cpu_bursts = list(cpu_bursts)
        self.io_bursts = list(io_bursts)
        self.priority = priority
        self.process_type = process_type
        
        # Execution State
        self.current_queue = 0
        self.total_cpu_time = sum(cpu_bursts)
        self.remaining_cpu_time = self.total_cpu_time
        
        # Metrics
        self.start_time: Optional[int] = None
        self.completion_time: Optional[int] = None
        self.response_time: Optional[int] = None
        self.waiting_time: int = 0
        self.turnaround_time: Optional[int] = None
        
        # Counters
        self.context_switches: int = 0
        self.preemptions: int = 0
        self.io_operations: int = 0
        
        # Starvation tracking
        self.starvation_status: bool = False
        self.last_cpu_time: int = arrival_time

    def is_completed(self) -> bool:
        return len(self.cpu_bursts) == 0

    def has_io(self) -> bool:
        """Returns True if the process has an impending I/O burst after its current CPU burst."""
        # A process only goes to I/O if there is an I/O burst matching the CPU burst it just finished.
        # Since CPU bursts are popped first, an I/O burst is typically aligned if len(cpu_bursts) == len(io_bursts).
        # Actually, standard is cpu1 -> io1 -> cpu2 -> io2 -> cpu3.
        # So io_bursts length is usually cpu_bursts length - 1.
        return len(self.io_bursts) > 0

    def get_next_cpu_burst(self) -> int:
        if self.cpu_bursts:
            return self.cpu_bursts[0]
        return 0

    def consume_cpu(self, time: int) -> int:
        """Consumes up to 'time' units of the current CPU burst. Returns actual time consumed."""
        if not self.cpu_bursts:
            return 0
            
        burst = self.cpu_bursts[0]
        consumed = min(burst, time)
        
        self.cpu_bursts[0] -= consumed
        self.remaining_cpu_time -= consumed
            
        return consumed

    def get_next_io_burst(self) -> int:
        if self.io_bursts:
            return self.io_bursts[0]
        return 0
        
    def consume_io(self) -> int:
        """Consumes the current I/O burst and returns its duration."""
        if not self.io_bursts:
            return 0
        self.io_operations += 1
        return self.io_bursts.pop(0)

    def calculate_metrics(self):
        """Calculates final turnaround and response times if completed."""
        if self.completion_time is not None:
            self.turnaround_time = self.completion_time - self.arrival_time
        if self.start_time is not None:
            self.response_time = self.start_time - self.arrival_time
            
    def to_dict(self):
        return {
            "pid": self.pid,
            "arrival_time": self.arrival_time,
            "priority": self.priority,
            "process_type": self.process_type.value,
            "total_cpu_time": self.total_cpu_time,
            "remaining_cpu_time": self.remaining_cpu_time,
            "current_queue": self.current_queue,
            "response_time": self.response_time,
            "completion_time": self.completion_time,
            "waiting_time": self.waiting_time,
            "turnaround_time": self.turnaround_time,
            "context_switches": self.context_switches,
            "preemptions": self.preemptions,
            "io_operations": self.io_operations,
            "starvation_status": self.starvation_status,
        }
