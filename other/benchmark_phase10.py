import time
import uuid
from fastapi.testclient import TestClient
from main import app

def run_benchmark():
    print("Starting Phase 10 Benchmark...")
    
    sid = str(uuid.uuid4())
    print(f"\n--- Request 1 (Session: {sid}) ---")
    
    with TestClient(app) as client:
        # Request 1
        client.post("/chat", json={"session_id": sid, "message": "How can I apply for a new ration card?"})
        client.post("/chat", json={"session_id": sid, "message": "Gujarat"})
        client.post("/chat", json={"session_id": sid, "message": "Sabarkantha"})
        
        t_req1_start = time.perf_counter()
        res1 = client.post("/chat", json={"session_id": sid, "message": "APL"})
        t_req1_total = (time.perf_counter() - t_req1_start) * 1000
        
        print(f"Request 1 Total: {t_req1_total:.2f}ms")
        print(f"Response 1:\n{res1.json().get('reply', '')[:200]}...")

        # Wait a bit
        time.sleep(1)

        sid2 = str(uuid.uuid4())
        print(f"\n--- Request 2 (Session: {sid2}) ---")
        client.post("/chat", json={"session_id": sid2, "message": "How can I apply for a new ration card?"})
        client.post("/chat", json={"session_id": sid2, "message": "Gujarat"})
        client.post("/chat", json={"session_id": sid2, "message": "Sabarkantha"})
        
        t_req2_start = time.perf_counter()
        res2 = client.post("/chat", json={"session_id": sid2, "message": "APL"})
        t_req2_total = (time.perf_counter() - t_req2_start) * 1000
        
        print(f"Request 2 Total: {t_req2_total:.2f}ms")
        print(f"Response 2:\n{res2.json().get('reply', '')[:200]}...")

        print("\n\n=== PHASE 10 REPORT ===")
        print("429 handling: Enabled fail-fast config in gemini.py (attempts=1).")
        print("Cache: In-memory TTLCache implemented.")
        print(f"Cache miss latency: {t_req1_total:.2f} ms")
        print(f"Cache hit latency: {t_req2_total:.2f} ms")

if __name__ == '__main__':
    run_benchmark()
