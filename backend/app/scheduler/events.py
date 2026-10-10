from enum import Enum
from typing import Any, Dict, Optional

class EventType(str, Enum):
    PROCESS_ARRIVAL = "PROCESS_ARRIVAL"
    CPU_START = "CPU_START"
    CPU_PREEMPTION = "CPU_PREEMPTION"
    QUANTUM_EXPIRED = "QUANTUM_EXPIRED"
    IO_START = "IO_START"
    IO_COMPLETE = "IO_COMPLETE"
    PROCESS_COMPLETION = "PROCESS_COMPLETION"
    PRIORITY_BOOST = "PRIORITY_BOOST"
    CONTEXT_SWITCH = "CONTEXT_SWITCH"
    
class Event:
    def __init__(self, time: int, event_type: EventType, pid: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        self.time = time
        self.event_type = event_type
        self.pid = pid
        self.details = details or {}

    def to_dict(self):
        return {
            "time": self.time,
            "event": self.event_type.value,
            "pid": self.pid,
            "details": self.details
        }
