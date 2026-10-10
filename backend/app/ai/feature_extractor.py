import statistics
from typing import List, Dict, Any
from app.scheduler.process import Process

class FeatureExtractor:
    @staticmethod
    def extract(process: Process) -> List[float]:
        """
        Extracts a feature vector from a process based on its original behaviour.
        Features:
        0: avg_cpu_burst
        1: avg_io_burst
        2: io_frequency
        3: cpu_io_ratio
        4: burst_variance
        5: preemption_count
        """
        cpu_bursts = process.original_cpu_bursts
        io_bursts = process.original_io_bursts
        
        avg_cpu = statistics.mean(cpu_bursts) if cpu_bursts else 0.0
        avg_io = statistics.mean(io_bursts) if io_bursts else 0.0
        
        io_freq = len(io_bursts) / len(cpu_bursts) if cpu_bursts else 0.0
        
        cpu_io_ratio = avg_cpu / avg_io if avg_io > 0 else avg_cpu
        
        variance = statistics.variance(cpu_bursts) if len(cpu_bursts) > 1 else 0.0
        
        preemptions = process.preemptions
        
        return [
            float(avg_cpu),
            float(avg_io),
            float(io_freq),
            float(cpu_io_ratio),
            float(variance),
            float(preemptions)
        ]
