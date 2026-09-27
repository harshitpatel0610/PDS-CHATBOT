import json

filepath = "chatbot/router/data/pds_intents.json"
with open(filepath, "r", encoding="utf-8") as f:
    data = json.load(f)

for intent in data["intents"]:
    if intent["intent"] == "ration_card_apply":
        intent.setdefault("patterns", []).extend([
            "where do i apply",
            "where to apply",
            "where can i apply"
        ])
        
with open(filepath, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("Updated patterns for ration_card_apply")
