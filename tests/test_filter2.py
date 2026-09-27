from rag.retriever import retriever

retriever.initialize()

print("Documents_required only:")
print(len(retriever.collection.get(where={"intent": "documents_required"})["ids"]))

print("State=Gujarat only:")
print(len(retriever.collection.get(where={"state": "Gujarat"})["ids"]))

print("Card_type=APL only:")
print(len(retriever.collection.get(where={"card_type": "APL"})["ids"]))

print("State+CardType+Intent:")
print(len(retriever.collection.get(where={
    "$and": [
        {"intent": "documents_required"},
        {"state": "Gujarat"},
        {"card_type": "APL"}
    ]
})["ids"]))
