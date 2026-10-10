from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import simulations, workloads

app = FastAPI(
    title="Adaptive MLFQ Scheduler API",
    description="Backend for the Adaptive Multilevel Feedback Queue Scheduling Research Project",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(simulations.router)
app.include_router(workloads.router)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Simulation Engine is running"}
