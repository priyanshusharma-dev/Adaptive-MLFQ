from typing import List, Dict, Any

def calculate_starvation_metrics(processes: List[Dict[str, Any]]) -> Dict[str, Any]:
    starved_count = 0
    starved_pids = []
    
    for p in processes:
        if p.get("starvation_status", False):
            starved_count += 1
            starved_pids.append(p.get("pid"))
            
    return {
        "starved_processes_count": starved_count,
        "starved_pids": starved_pids
    }
