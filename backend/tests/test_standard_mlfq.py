import pytest
from app.scheduler.process import Process
from app.scheduler.queue import Queue
from app.scheduler.standard_mlfq import StandardMLFQScheduler

def test_standard_mlfq_basic():
    q0 = Queue(0, 0, 4)
    q1 = Queue(1, 1, 8)
    q2 = Queue(2, 2, 16)
    
    scheduler = StandardMLFQScheduler([q0, q1, q2], starvation_threshold=50, priority_boost_interval=100)
    
    # Process with 10 ms CPU burst
    p1 = Process("P1", arrival_time=0, cpu_bursts=[10], io_bursts=[])
    
    results = scheduler.run([p1])
    
    # Check results
    assert len(results["processes"]) == 1
    p1_res = results["processes"][0]
    
    # Execution:
    # t=0 -> enters Q0
    # Q0 quantum is 4. Runs t=0 to t=4. Burst remaining = 6. Demoted to Q1.
    # Q1 quantum is 8. Runs t=4 to t=10. Burst remaining = 0. Completed.
    assert p1_res["completion_time"] == 10
    assert p1_res["turnaround_time"] == 10
    assert p1_res["response_time"] == 0
    
    gantt = results["gantt"]
    assert len(gantt) == 2
    assert gantt[0]["queue"] == 0
    assert gantt[0]["start"] == 0
    assert gantt[0]["end"] == 4
    
    assert gantt[1]["queue"] == 1
    assert gantt[1]["start"] == 4
    assert gantt[1]["end"] == 10

def test_standard_mlfq_io():
    q0 = Queue(0, 0, 4)
    q1 = Queue(1, 1, 8)
    
    scheduler = StandardMLFQScheduler([q0, q1], starvation_threshold=50, priority_boost_interval=100)
    
    # p1: cpu=2, io=4, cpu=2
    p1 = Process("P1", arrival_time=0, cpu_bursts=[2, 2], io_bursts=[4])
    
    results = scheduler.run([p1])
    p1_res = results["processes"][0]
    
    # t=0 to 2: Q0 CPU
    # t=2 to 6: IO
    # t=6 to 8: Q0 CPU
    # Completion time = 8
    
    assert p1_res["completion_time"] == 8
    assert p1_res["turnaround_time"] == 8
