from google import genai
import sys

try:
    client = genai.Client(api_key="DUMMY_KEY", http_options={'retry_options': {'attempts': 1}})
    print("Success")
except Exception as e:
    print(repr(e))
