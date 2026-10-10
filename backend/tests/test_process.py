import pytest
from app.scheduler.process import Process, ProcessType

def test_process_initialization():
    p = Process(
        pid="P1",
        arrival_time=0,
        cpu_bursts=[8, 5, 12],
        io_bursts=[4, 6],
        process_type=ProcessType.CPU_BOUND
    )
    
    assert p.pid == "P1"
    assert p.total_cpu_time == 25
    assert p.remaining_cpu_time == 25
    assert not p.is_completed()

def test_process_consume_cpu():
    p = Process(
        pid="P1",
        arrival_time=0,
        cpu_bursts=[8],
        io_bursts=[]
    )
    
    # Consume partial burst
    consumed = p.consume_cpu(5)
    assert consumed == 5
    assert p.remaining_cpu_time == 3
    assert not p.is_completed()
    
    # Consume rest of the burst
    consumed2 = p.consume_cpu(5)
    assert consumed2 == 3
    assert p.remaining_cpu_time == 0
    p.cpu_bursts.pop(0) # Emulate scheduler popping it
    assert p.is_completed()

def test_process_metrics():
    p = Process(
        pid="P1",
        arrival_time=2,
        cpu_bursts=[10],
        io_bursts=[]
    )
    p.start_time = 5
    p.completion_time = 15
    p.calculate_metrics()
    
    assert p.response_time == 3
    assert p.turnaround_time == 13
