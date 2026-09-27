import json

filepath = "chatbot/router/data/pds_intents.json"
with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

for intent in data["intents"]:
    name = intent["intent"]
    
    if name == "contact_admin":
        intent.setdefault("examples", []).extend([
            "Who is the ration card officer?",
            "Which office verifies my documents?",
            "Which official handles ration card issues?",
            "Who is responsible for ration card applications?",
            "Who should I contact at the ration office for verification?",
            "Which department is in charge of PDS cards?",
            "Where is the local food inspector office?"
        ])
        
    elif name == "pds_helpline":
        intent.setdefault("examples", []).extend([
            "Who should I contact for ration card application queries?",
            "Where can I call for help with my application?",
            "Is there a customer care number for PDS?",
            "Who can I speak to about application problems?"
        ])
        
    elif name == "file_complaint":
        intent.setdefault("examples", []).extend([
            "Who handles ration card complaints?",
            "Where do I report a problem with the dealer?",
            "Which official takes care of grievances?",
            "Who do I contact to file a formal complaint?"
        ])
        
    elif name == "ration_card_apply":
        intent.setdefault("examples", []).extend([
            "Where can I submit my documents?",
            "How do I upload documents online for application?",
            "Where do I hand in the paperwork?",
            "How do I submit the application forms and proofs?",
            "What is the procedure to upload the required files?"
        ])
        
    elif name == "ration_card_status":
        intent.setdefault("examples", []).extend([
            "What happens after document verification?",
            "What is the next step after I submit my documents?",
            "How long after verification will I get the card?",
            "My documents are verified, what is the status now?"
        ])
        
    elif name == "ration_card_update":
        intent.setdefault("examples", []).extend([
            "Can I update my Aadhaar document after applying?",
            "How do I change the Aadhaar proof on my card?",
            "I need to upload a new document for correction.",
            "Can I replace the uploaded documents for my existing card?"
        ])

with open(filepath, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("Updated pds_intents.json with new semantic examples.")
