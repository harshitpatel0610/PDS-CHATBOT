from chatbot.router.rules import classify_by_rules

queries = [
    "Can I get a ration card without Aadhaar?",
    "Who is eligible for APL ration card?",
    "Who can get an APL ration card?",
    "How can I apply for a ration card online?"
]
for q in queries:
    res = classify_by_rules(q)
    print(f"Query: {q}")
    print(f"Rule Intent: {res.intent}, Confidence: {res.confidence}\n")
