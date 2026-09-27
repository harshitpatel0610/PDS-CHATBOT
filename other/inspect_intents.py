import json
with open("chatbot/router/data/pds_intents.json", "r") as f:
    data = json.load(f)
for i in data["intents"]:
    if i["intent"] in ["documents_required", "ration_card_types"]:
        print(f"Intent: {i['intent']}")
        print(f"Keywords: {i.get('keywords', [])}")
        print(f"Patterns: {i.get('patterns', [])}")
        print("-" * 40)
