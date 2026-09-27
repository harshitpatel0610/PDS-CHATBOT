from chatbot.router.service import RoutingService

queries = [
    "Can I apply online without Aadhaar?",
    "Who is eligible and can they apply online?",
    "How can I apply for APL?",
    "What documents are required to apply for APL ration card?",
    "Who is the ration card officer?",
    "Can I update my Aadhaar document after applying?",
    "Which office verifies my documents?",
    "Can I apply for APL?",
]

for q in queries:
    res = RoutingService.classify(q)
    print(f"\nQUERY: {q}")
    print(f"FINAL: {res.intent} (conf: {res.confidence})")
