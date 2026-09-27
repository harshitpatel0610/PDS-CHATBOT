def detect_context(query):
    query = query.lower()
    
    eligibility_context = any(phrase in query for phrase in [
        "who can", "who is", "am i eligible", "who qualifies", "who gets", "eligibility", "eligible", "qualify", "qualifies", "allowed to"
    ])
    
    document_context = any(phrase in query for phrase in [
        "document", "proof", "paperwork", "compulsory", "mandatory", "required"
    ]) or ("aadhaar" in query.replace("adhaar", "aadhaar") and any(phrase in query for phrase in [
        "without", "don't have", "do not have", "no aadhaar", "no adhaar", "nahi hai"
    ]))

    print(f"[{'E' if eligibility_context else ' '}] [{'D' if document_context else ' '}] {query}")

queries = [
    "Aadhaar nahi hai to ration card ke liye apply kar sakte hai?",
]

for q in queries:
    detect_context(q)
