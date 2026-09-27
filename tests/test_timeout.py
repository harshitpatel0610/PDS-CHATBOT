import requests

try:
    response = requests.post(
        "http://127.0.0.1:8000/chat",
        json={
            "session_id": "test_124",
            "message": "What documents are required to apply for a ration card in Gujarat?"
        },
        timeout=30
    )
    print("Status:", response.status_code)
except Exception as e:
    print("Exception:", repr(e))
