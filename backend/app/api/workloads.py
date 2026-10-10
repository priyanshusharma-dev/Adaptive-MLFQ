from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
from app.schemas.simulation import ProcessConfig
from app.services.workload_generator import WorkloadGenerator

router = APIRouter(prefix="/api/workloads", tags=["workloads"])

class GenerateWorkloadRequest(BaseModel):
    type: str = "mixed" # cpu_heavy, io_heavy, interactive, mixed
    count: int = 10
    seed: int = 42

@router.post("/generate", response_model=List[ProcessConfig])
def generate_workload(req: GenerateWorkloadRequest):
    processes = WorkloadGenerator.generate(
        workload_type=req.type,
        num_processes=req.count,
        seed=req.seed
    )
    return processes
