from chatbot.router.service import RoutingService

queries = {
    "Eligibility": [
        "Who is the ration card officer?",
        "Who can get an APL ration card?",
        "Who is eligible for APL?",
        "Am I eligible to apply for APL?",
        "Who handles ration card complaints?"
    ],
    "Documents": [
        "What documents are required for APL?",
        "Is Aadhaar mandatory for APL?",
        "Can I apply without Aadhaar?",
        "Where can I submit my documents?",
        "Which office verifies my documents?",
        "Can I update my Aadhaar document?"
    ],
    "Application": [
        "How do I apply for APL?",
        "Where do I apply?",
        "How can I apply online?",
        "How can I apply offline?"
    ],
    "Online/offline": [
        "Is the application online or offline?",
        "Can I apply online or offline?"
    ],
    "Types": [
        "What is APL?",
        "What is BPL?",
        "Is APL different from BPL?"
    ],
    "Hinglish": [
        "APL ke liye kon eligible hai?",
        "APL ke liye kon apply kar sakta hai?",
        "APL ke liye kya document chahiye?",
        "Aadhar nhi hai to apply kar skte hai?",
        "ration card online banega ya offline?",
        "ration card ke liye kaha apply kare?"
    ]
}

for category, q_list in queries.items():
    print(f"\n--- {category} ---")
    for q in q_list:
        res = RoutingService.classify(q)
        print(f"'{q}' -> {res.intent}")
