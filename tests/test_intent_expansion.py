from chatbot.conversation.session import ConversationSession
from chatbot.entities.extractor import EntityExtractor
from rag.retriever import retriever

query = "What documents are required to apply for a ration card in Gujarat?"
intent = "documents_required"
state = "Gujarat"

# Simulate modified retrieval
intent_list = ["documents_required", "ration_card_apply"]

where_filter = {
    "$and": [
        {"intent": {"$in": intent_list}},
        {"state": state}
    ]
}

retriever.initialize()
from rag.embeddings import embedding_service
query_embedding = embedding_service.embed_text(query)

results = retriever.collection.query(
    query_embeddings=[query_embedding],
    n_results=5,
    where=where_filter
)

print("\n--- RETRIEVED CONTEXT ---")
docs = results.get("documents", [[]])[0]
metas = results.get("metadatas", [[]])[0]
for i, (doc, meta) in enumerate(zip(docs, metas)):
    print(f"\n[Doc {i}]")
    print(f"Meta: {meta}")
    print(f"Content: {doc}")
