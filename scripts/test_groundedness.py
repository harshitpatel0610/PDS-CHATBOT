import sys
from fastapi.testclient import TestClient
from main import app
import uuid

def test_groundedness(query, expected_in_response, expected_not_in_response, state):
    with TestClient(app) as client:
        sid = str(uuid.uuid4())
        print(f"Testing Query: {query}")
        # Prime the session with state
        client.post("/chat", json={"session_id": sid, "message": state})
        
        res = client.post("/chat", json={"session_id": sid, "message": query})
        if res.status_code != 200:
            print("FAILED: HTTP", res.status_code)
            return False
            
        response = res.json().get("reply", "")
        print("Response:")
        print(response.encode('ascii', 'ignore').decode('ascii'))
    
    passed = True
    for expected in expected_in_response:
        if expected.lower() not in response.lower():
            print(f"FAILED: Expected '{expected}' in response.")
            passed = False
            
    for not_expected in expected_not_in_response:
        if not_expected.lower() in response.lower():
            print(f"FAILED: Did NOT expect '{not_expected}' in response.")
            passed = False
            
    if passed:
        print("PASS")
    else:
        print("FAIL")
    return passed

if __name__ == "__main__":
    passed = 0
    
    print("=== TEST 1 ===")
    if test_groundedness("How can I apply for a ration card in Gujarat?", ["digital gujarat", "online"], [], "I am from Sabarkantha, Gujarat with an APL card."): passed += 1
    
    print("\n=== TEST 2 ===")
    if test_groundedness("Can I apply for a new ration card online in Gujarat?", ["digital gujarat", "online"], [], "I am from Sabarkantha, Gujarat with an APL card."): passed += 1
    
    print("\n=== TEST 3 ===")
    if test_groundedness("Where can I get the Gujarat ration card application form?", ["form-2"], [], "I am from Sabarkantha, Gujarat with an APL card."): passed += 1
    
    print("\n=== TEST 4 ===")
    if test_groundedness("How much does a new Gujarat ration card cost?", ["free", "rs. 20"], [], "I am from Sabarkantha, Gujarat with an APL-1 card."): passed += 1
    
    print("\n=== TEST 5 ===")
    if test_groundedness("What documents are required for a new Gujarat ration card?", ["election", "proof"], ["passport"], "I am from Sabarkantha, Gujarat with an APL card."): passed += 1
    
    print("\n=== TEST 6 ===")
    if test_groundedness("How long does it take to get a Gujarat ration card?", ["15"], ["30 days"], "I am from Sabarkantha, Gujarat with an APL card."): passed += 1
    
    print("\n=== TEST 7 ===")
    if test_groundedness("Where can I submit the Gujarat ration card application?", ["e-gram", "taluka", "zonal"], [], "I am from Sabarkantha, Gujarat with an APL card."): passed += 1

    print(f"\nPassed {passed}/7 tests.")
    if passed == 7:
        import sys
        sys.exit(0)
    else:
        import sys
        sys.exit(1)
