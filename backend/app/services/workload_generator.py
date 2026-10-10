import random
import uuid
from typing import List
from app.schemas.simulation import ProcessConfig

class WorkloadGenerator:
    @staticmethod
    def generate(
        workload_type: str, 
        num_processes: int,
        seed: int = 42
    ) -> List[ProcessConfig]:
        random.seed(seed)
        processes = []

        for i in range(num_processes):
            pid = f"P{i+1}"
            arrival_time = random.randint(0, num_processes * 2)
            
            # Default profiles
            if workload_type == "cpu_heavy":
                # Few, very long CPU bursts, little to no IO
                cpu_bursts = [random.randint(20, 100) for _ in range(random.randint(1, 3))]
                io_bursts = [random.randint(1, 5) for _ in range(len(cpu_bursts) - 1)]
                
            elif workload_type == "io_heavy":
                # Many short CPU bursts separated by long IO
                num_bursts = random.randint(5, 15)
                cpu_bursts = [random.randint(1, 5) for _ in range(num_bursts)]
                io_bursts = [random.randint(20, 50) for _ in range(num_bursts - 1)]
                
            elif workload_type == "interactive":
                # Many short CPU bursts, short IO (user input)
                num_bursts = random.randint(10, 20)
                cpu_bursts = [random.randint(1, 4) for _ in range(num_bursts)]
                io_bursts = [random.randint(5, 15) for _ in range(num_bursts - 1)]
                
            else: # Mixed
                choice = random.choice(["cpu_heavy", "io_heavy", "interactive"])
                return WorkloadGenerator.generate(choice, 1, seed + i) # recurse for single process logic
                
            processes.append(
                ProcessConfig(
                    pid=pid,
                    arrival_time=arrival_time,
                    cpu_bursts=cpu_bursts,
                    io_bursts=io_bursts
                )
            )

        # Sort by arrival time
        processes.sort(key=lambda p: p.arrival_time)
        return processes
