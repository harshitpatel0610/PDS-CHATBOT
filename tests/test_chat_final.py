import requests

query = "What documents are required to apply for a ration card in Gujarat?"
try:
    response = requests.post(
        "http://127.0.0.1:8000/chat",
        json={
            "session_id": "test_125",
            "message": query
        },
        timeout=120
    )
    print("Status:", response.status_code)
    print("Response:", response.text)
except Exception as e:
    print("Exception:", repr(e))
