import sys
from fastapi.testclient import TestClient
from main import app
import time

def test_query(client, query, expected_in, expected_out=None, session_id=None):
    if session_id is None:
        session_id = str(time.time())
    
    print(f"Testing Query: {query}")
    res = client.post("/chat", json={"session_id": session_id, "message": query})
    if res.status_code != 200:
        print(f"FAILED: Status {res.status_code}")
        return False
        
    response = res.json().get("reply", "")
    print("Response:")
    print(response.encode('ascii', 'ignore').decode('ascii'))
    
    response_lower = response.lower()
    
    passed = True
    for exp in expected_in:
        if exp.lower() not in response_lower:
            print(f"FAILED: Expected '{exp}' in response.")
            passed = False
            
    if expected_out:
        for exp in expected_out:
            if exp.lower() in response_lower:
                print(f"FAILED: Expected '{exp}' NOT to be in response.")
                passed = False
                
    if passed:
        print("PASS\n")
    else:
        print("FAIL\n")
        
    return passed

if __name__ == "__main__":
    with TestClient(app) as client:
        passed = 0
        
        print("=== TEST 1 ===")
        # Intent: ration_card_apply, entities: state, card_type
        # Expected: No district clarification, answers the fee question
        if test_query(client, "What is the fee for an APL ration card in Gujarat?", ["rs. 20"], ["district"]): passed += 1
        
        print("=== TEST 2 ===")
        # Intent: ration_card_apply, entities: state
        # Expected: No district clarification, might ask for card type, but if answer is generated, should contain apply info
        if test_query(client, "How can I apply for a ration card in Gujarat?", ["digital gujarat", "online"], ["district"]): passed += 1
        
        print("=== TEST 3 ===")
        if test_query(client, "What documents are required for a Gujarat ration card?", ["election", "proof"], ["district"]): passed += 1
        
        print("=== TEST 4 ===")
        if test_query(client, "What is the fee for an APL ration card in Sabarkantha, Gujarat?", ["rs. 20"], ["district"]): passed += 1
        
        print("=== TEST 5 ===")
        if test_query(client, "What is the fee for an APL ration card in Gujarat?", ["rs. 20"], ["district"]): passed += 1
        
        print(f"\nPassed {passed}/5 tests.")
        if passed == 5:
            sys.exit(0)
        else:
            sys.exit(1)
