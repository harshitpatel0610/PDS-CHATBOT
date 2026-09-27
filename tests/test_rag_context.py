from chatbot.conversation.session import ConversationSession
from chatbot.services.rag_service import RAGService
from chatbot.router.router import route
from chatbot.entities.extractor import EntityExtractor
from rag.retriever import retriever

query = "What documents are required to apply for a ration card in Gujarat?"

# Route
route_res = route(query)
intent = route_res.intent
print("Intent:", intent)

# Extract
entities = EntityExtractor.extract(query, intent)
session = ConversationSession(session_id="test")
session.current_intent = intent
for e in entities:
    session.entities[e.entity_type] = e.value
print("Entities:", session.entities)

# Retrieve
state = session.entities.get("states")
card_type = session.entities.get("card_types")

result = retriever.search(
    query=query,
    top_k=5,
    intent=intent,
    state=state,
    card_type=card_type
)

print("Retrieval Level:", result.get("retrieval_level"))

docs = result.get("documents", [[]])[0]
metas = result.get("metadatas", [[]])[0]

print("\n--- RETRIEVED CONTEXT ---")
for i, (doc, meta) in enumerate(zip(docs, metas)):
    print(f"\n[Doc {i}]")
    print(f"Meta: {meta}")
    print(f"Content: {doc}")

