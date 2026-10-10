from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class ProcessConfig(BaseModel):
    pid: str
    arrival_time: int = 0
    cpu_bursts: List[int]
    io_bursts: List[int] = []

class QueueConfig(BaseModel):
    id: int
    quantum: Optional[int] = None

class SimulationRequest(BaseModel):
    mode: str = Field(default="standard", description="standard or adaptive")
    queues: List[QueueConfig]
    processes: List[ProcessConfig]
    starvation_threshold: int = 50
    priority_boost_interval: int = 100
    context_switch_cost: int = 0

class SimulationResponse(BaseModel):
    simulation_id: str
    gantt: List[Dict[str, Any]]
    process_metrics: List[Dict[str, Any]]
    system_metrics: Dict[str, Any]
    events: List[Dict[str, Any]]
    adaptive_decisions: Optional[List[Dict[str, Any]]] = []
