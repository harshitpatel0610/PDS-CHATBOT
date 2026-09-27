from chatbot.router.rules import classify_by_rules
res = classify_by_rules("Ration card online banega ya offline? for a new ration card")
print(res.intent, res.confidence)
