import json
data = json.load(open("chatbot/router/data/pds_intents.json", encoding="utf-8"))
intents_to_check = ["contact_admin", "file_complaint", "ration_card_apply", "ration_card_status", "ration_card_update", "pds_helpline"]
for intent in data["intents"]:
    if intent["intent"] in intents_to_check:
        print(f"=== {intent['intent']} ===")
        print(f"Patterns: {len(intent.get('patterns', []))} Examples: {len(intent.get('examples', []))}")
        print("Negative patterns:", intent.get("negative_patterns", []))
