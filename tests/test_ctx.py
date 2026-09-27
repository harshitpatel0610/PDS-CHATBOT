def detect_context(query):
    query = query.lower()
    
    eligibility_context = any(phrase in query for phrase in [
        "who can", "who is", "am i eligible", "who qualifies", "who gets", "eligibility", "eligible", "qualify", "qualifies"
    ])
    
    document_context = any(phrase in query for phrase in [
        "document", "proof", "paperwork", "compulsory", "mandatory", "required"
    ]) or ("aadhaar" in query.replace("adhaar", "aadhaar") and any(phrase in query for phrase in [
        "without", "don't have", "do not have", "no aadhaar", "no adhaar"
    ]))

    print(f"[{'E' if eligibility_context else ' '}] [{'D' if document_context else ' '}] {query}")

queries = [
    "Can I get a ration card without Aadhaar?",
    "I don't have Aadhaar, can I apply for ration card?",
    "Aadhaar nahi hai to ration card ke liye apply kar sakte hai?",
    "Is Aadhaar compulsory for APL ration card?",
    "What documents are required to apply for APL ration card?",
    "Who is eligible for APL ration card?",
    "Who can get an APL ration card?",
    "Who qualifies for BPL ration card?",
    "Who is allowed to apply for BPL ration card?",
    "Can I qualify for APL ration card?",
    "What are the eligibility criteria for BPL ration card?",
    "Am I eligible for an APL ration card?",
    "How can I apply for a ration card online?",
    "Who can apply for APL and what documents are required?",
    "Who is eligible to apply for APL ration card?",
    "Who can apply for BPL ration card and what is the process?",
    "Can I apply for APL ration card without Aadhaar?",
    "what are the types of ration cards?",
    "is BPL a type of ration card?"
]

for q in queries:
    detect_context(q)
