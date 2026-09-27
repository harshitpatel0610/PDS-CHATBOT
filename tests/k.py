import json
data = json.load(open("chatbot/router/data/pds_intents.json", encoding="utf-8"))
for i in data["intents"]:
    if i["intent"] in ["ration_card_apply", "ration_card_eligibility"]:
        print(f"[{i['intent']}] Keywords: {i.get('keywords', [])}")
