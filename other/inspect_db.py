from rag.retriever import retriever

retriever.initialize()
collection = retriever.collection
res = collection.get(include=["metadatas"])

intents = set()
states = set()
categories = set()

for m in res["metadatas"]:
    if "intent" in m:
        intents.add(m["intent"])
    if "state" in m:
        states.add(m["state"])
    if "category" in m:
        categories.add(m["category"])
        
print("Intents:", intents)
print("States:", states)
print("Categories:", categories)
print("Total docs:", len(res["ids"]))
