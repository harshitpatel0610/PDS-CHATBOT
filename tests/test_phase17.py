from chatbot.router.router import RoutingService

router = RoutingService()

queries = [
    "Is Aadhaar mandatory for applying APL ration card in Gujarat?",
    "What documents are required for APL ration card in Gujarat?",
    "Do I need Aadhaar for a new ration card?",
    "What types of ration cards are available in Gujarat?",
    "What is APL and BPL ration card?",
    "Which ration card category should I apply for?"
]

print("Targeted Test Results:\n" + "="*50)
for query in queries:
    res = router.classify(query)
    print(f"Q: {query}")
    print(f"I: {res.intent} (Score: {res.confidence:.2f})\n")
