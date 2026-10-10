import pytest
from app.scheduler.process import Process
from app.scheduler.queue import Queue

def test_queue_operations():
    q = Queue(queue_id=1, priority=1, quantum=8)
    p1 = Process("P1", 0, [5], [])
    p2 = Process("P2", 1, [10], [])
    
    assert q.is_empty()
    
    q.enqueue(p1)
    q.enqueue(p2)
    
    assert not q.is_empty()
    assert q.size() == 2
    assert p1.current_queue == 1
    
    popped = q.dequeue()
    assert popped.pid == "P1"
    assert q.size() == 1
    
def test_queue_remove_process():
    q = Queue(0, 0, 4)
    p1 = Process("P1", 0, [5], [])
    p2 = Process("P2", 1, [10], [])
    
    q.enqueue(p1)
    q.enqueue(p2)
    
    removed = q.remove_process("P2")
    assert removed.pid == "P2"
    assert q.size() == 1
    
    all_procs = q.get_all_processes()
    assert len(all_procs) == 1
    assert q.is_empty()
