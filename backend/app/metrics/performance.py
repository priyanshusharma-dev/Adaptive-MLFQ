from typing import List, Dict, Any

def calculate_performance_metrics(processes: List[Dict[str, Any]], total_time: int) -> Dict[str, float]:
    if not processes:
        return {
            "avg_waiting_time": 0.0,
            "avg_response_time": 0.0,
            "avg_turnaround_time": 0.0,
            "throughput": 0.0,
            "total_context_switches": 0
        }

    total_waiting = 0
    total_response = 0
    total_turnaround = 0
    total_context_switches = 0
    completed_count = 0

    for p in processes:
        total_waiting += p.get("waiting_time", 0)
        total_context_switches += p.get("context_switches", 0)
        
        if p.get("completion_time") is not None:
            completed_count += 1
            total_turnaround += p.get("turnaround_time", 0)
            
        if p.get("response_time") is not None:
            total_response += p.get("response_time", 0)

    n = len(processes)
    
    # Throughput is completed processes per unit time. We might scale it (e.g. per 100ms)
    throughput = (completed_count / total_time) if total_time > 0 else 0

    return {
        "avg_waiting_time": total_waiting / n,
        "avg_response_time": total_response / n,
        "avg_turnaround_time": total_turnaround / completed_count if completed_count > 0 else 0,
        "throughput": throughput,
        "total_context_switches": total_context_switches
    }
