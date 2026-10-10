from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_run_simulation():
    payload = {
        "mode": "standard",
        "queues": [
            {"id": 0, "quantum": 4},
            {"id": 1, "quantum": 8}
        ],
        "processes": [
            {
                "pid": "P1",
                "arrival_time": 0,
                "cpu_bursts": [10],
                "io_bursts": []
            }
        ]
    }
    
    response = client.post("/api/simulations/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "simulation_id" in data
    assert "system_metrics" in data
    assert data["system_metrics"]["total_time"] >= 10
