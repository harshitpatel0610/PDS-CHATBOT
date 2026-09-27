import json
from chatbot.router.service import RoutingService

queries = [
    ("Can I get a ration card without Aadhaar?", "documents_required"),
    ("I don't have Aadhaar, can I apply for ration card?", "documents_required"),
    ("Aadhaar nahi hai to ration card ke liye apply kar sakte hai?", "documents_required"),
    ("Is Aadhaar compulsory for APL ration card?", "documents_required"),
    ("What documents are required to apply for APL ration card?", "documents_required"),
    ("Who is eligible for APL ration card?", "ration_card_eligibility"),
    ("Who can get an APL ration card?", "ration_card_eligibility"),
    ("Who qualifies for BPL ration card?", "ration_card_eligibility"),
    ("Who is allowed to apply for BPL ration card?", "ration_card_eligibility"),
    ("Can I qualify for APL ration card?", "ration_card_eligibility"),
    ("What are the eligibility criteria for BPL ration card?", "ration_card_eligibility"),
    ("Am I eligible for an APL ration card?", "ration_card_eligibility"),
    ("How can I apply for a ration card online?", "ration_card_apply"),
    ("Who can apply for APL and what documents are required?", "ration_card_eligibility"),
    ("Who is eligible to apply for APL ration card?", "ration_card_eligibility"),
    ("Who can apply for BPL ration card and what is the process?", "ration_card_eligibility"),
    ("Can I apply for APL ration card without Aadhaar?", "documents_required")
]

def run_tests():
    failed = 0
    print("=" * 60)
    for q, exp in queries:
        res = RoutingService.classify(q)
        if res.intent != exp:
            print(f"FAILED: '{q}'\n  Expected: {exp}\n  Actual: {res.intent} (conf: {res.confidence})\n")
            failed += 1
    
    print("Total:", len(queries))
    print("Failed:", failed)
    print("Passed:", len(queries) - failed)

if __name__ == '__main__':
    run_tests()
