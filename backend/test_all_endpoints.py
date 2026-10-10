import urllib.request
import urllib.parse
import json
import time

BASE_URL = "http://localhost:8000/api"

def make_request(url, data=None):
    if data:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'}, method='POST')
    else:
        req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as response:
        return json.loads(response.read().decode())

def run_tests():
    print("Testing Health...")
    r = make_request(f"{BASE_URL}/health")
    print(r)
    
    print("\nTesting Workload Generation...")
    processes = make_request(f"{BASE_URL}/workloads/generate", data={
        "type": "mixed",
        "count": 5,
        "seed": 42
    })
    print(f"Generated {len(processes)} processes")
    
    print("\nTesting Standard Simulation...")
    payload = {
        "mode": "standard",
        "queues": [
            {"id": 0, "quantum": 4},
            {"id": 1, "quantum": 8},
            {"id": 2, "quantum": 16}
        ],
        "processes": processes,
        "starvation_threshold": 50,
        "priority_boost_interval": 100,
        "context_switch_cost": 1
    }
    res = make_request(f"{BASE_URL}/simulations/run", data=payload)
    print(f"Standard Total Time: {res['system_metrics']['total_time']}ms")
    
    print("\nTesting Adaptive Simulation...")
    payload["mode"] = "adaptive"
    res2 = make_request(f"{BASE_URL}/simulations/run", data=payload)
    print(f"Adaptive Total Time: {res2['system_metrics']['total_time']}ms")
    print(f"Adaptive Decisions Logged: {len(res2.get('adaptive_decisions', []))}")
    
    print("\nAll endpoints working correctly!")

if __name__ == "__main__":
    run_tests()
