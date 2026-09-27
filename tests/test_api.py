import requests

query = "What documents are required to apply for a ration card in Gujarat?"
response = requests.post(
    "http://127.0.0.1:8000/chat",
    json={
        "session_id": "test_123",
        "message": query
    }
)
print("Status Code:", response.status_code)
print("Response:", response.text)
