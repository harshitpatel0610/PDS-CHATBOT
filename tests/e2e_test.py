from fastapi.testclient import TestClient
from main import app
import uuid

def run_e2e():
    sid = str(uuid.uuid4())
    print(f"Starting E2E Session: {sid}")

    messages = [
        "How can I apply for a new ration card?",
        "Gujarat",
        "Sabarkantha",
        "APL",
        "APL"  # Add one more to verify second APL latency as requested
    ]

    with TestClient(app) as client:
        for msg in messages:
            print(f"\nUser: {msg}")
            res = client.post("/chat", json={"session_id": sid, "message": msg})
            
            if res.status_code == 200:
                reply = res.json()["reply"]
                print(f"Assistant: {reply}")
            else:
                print(f"Error {res.status_code}: {res.text}")
                break

if __name__ == "__main__":
    run_e2e()
