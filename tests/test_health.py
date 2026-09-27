import requests

try:
    response = requests.get("http://127.0.0.1:8000/health")
    print("Health Status:", response.status_code)
except Exception as e:
    print("Exception:", repr(e))
