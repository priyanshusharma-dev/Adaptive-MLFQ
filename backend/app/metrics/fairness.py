from typing import List, Dict, Any

def calculate_jains_fairness_index(processes: List[Dict[str, Any]]) -> float:
    """
    Calculates Jain's Fairness Index based on normalized turnaround time 
    (Turnaround Time / Total CPU Time).
    
    J = (Σxi)^2 / (n × Σxi²)
    
    where xi is the normalized metric for process i.
    """
    if not processes:
        return 1.0

    n = len(processes)
    sum_x = 0.0
    sum_x_sq = 0.0

    for p in processes:
        # We use turnaround time over cpu time to measure fairness of execution speed
        # If turnaround time is missing, we use waiting time or a fallback
        turnaround = p.get("turnaround_time")
        cpu_time = p.get("total_cpu_time", 1)
        
        if turnaround is None:
            # Process didn't finish; approximate based on waiting time vs cpu time
            xi = 1.0 / (p.get("waiting_time", 0) + 1) 
        else:
            # Lower turnaround/cpu ratio is better. We invert it so higher is better for Jain's.
            ratio = turnaround / cpu_time if cpu_time > 0 else 1.0
            xi = 1.0 / ratio if ratio > 0 else 1.0

        sum_x += xi
        sum_x_sq += xi * xi

    if sum_x_sq == 0:
        return 1.0

    jains_index = (sum_x * sum_x) / (n * sum_x_sq)
    return round(jains_index, 4)
