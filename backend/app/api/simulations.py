import uuid
from fastapi import APIRouter, HTTPException
from app.schemas.simulation import SimulationRequest, SimulationResponse
from app.scheduler.process import Process
from app.scheduler.queue import Queue
from app.scheduler.standard_mlfq import StandardMLFQScheduler
from app.scheduler.adaptive_mlfq import AdaptiveMLFQScheduler
from app.metrics import calculate_performance_metrics, calculate_jains_fairness_index, calculate_starvation_metrics

router = APIRouter(prefix="/api/simulations", tags=["simulations"])

@router.post("/run", response_model=SimulationResponse)
def run_simulation(req: SimulationRequest):
    if not req.processes:
        raise HTTPException(status_code=400, detail="At least one process is required.")
        
    # Build queues
    queues = []
    for q in sorted(req.queues, key=lambda x: x.id):
        queues.append(Queue(queue_id=q.id, priority=q.id, quantum=q.quantum))
        
    # Build processes
    processes = []
    for p in req.processes:
        processes.append(
            Process(
                pid=p.pid,
                arrival_time=p.arrival_time,
                cpu_bursts=p.cpu_bursts,
                io_bursts=p.io_bursts
            )
        )
        
    # Select scheduler
    if req.mode.lower() == "standard":
        scheduler = StandardMLFQScheduler(
            queues=queues,
            starvation_threshold=req.starvation_threshold,
            priority_boost_interval=req.priority_boost_interval,
            context_switch_cost=req.context_switch_cost
        )
    else:
        scheduler = AdaptiveMLFQScheduler(
            queues=queues,
            starvation_threshold=req.starvation_threshold,
            priority_boost_interval=req.priority_boost_interval,
            context_switch_cost=req.context_switch_cost
        )
        
    # Run
    results = scheduler.run(processes)
    
    # Calculate metrics
    perf = calculate_performance_metrics(results["processes"], scheduler.time)
    fairness = calculate_jains_fairness_index(results["processes"])
    starvation = calculate_starvation_metrics(results["processes"])
    
    system_metrics = {
        **perf,
        "fairness_score": fairness,
        **starvation,
        "total_time": scheduler.time
    }
    
    return SimulationResponse(
        simulation_id=str(uuid.uuid4()),
        gantt=results["gantt"],
        process_metrics=results["processes"],
        system_metrics=system_metrics,
        events=results["events"],
        adaptive_decisions=results.get("adaptive_decisions", [])
    )
