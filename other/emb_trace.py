from chatbot.router.embeddings import initialize, classify_by_embeddings

initialize()

queries = [
    "Can I get a ration card without Aadhaar?",
    "I don't have Aadhaar, can I apply for ration card?",
    "Is Aadhaar compulsory for APL ration card?",
    "Who is eligible for APL ration card?",
    "Who can get an APL ration card?",
    "Who qualifies for BPL ration card?",
    "How can I apply for a ration card online?"
]
for q in queries:
    res = classify_by_embeddings(q)
    print(f"Query: {q}")
    print(f"Embedding Intent: {res.intent}, Confidence: {res.confidence}\n")
