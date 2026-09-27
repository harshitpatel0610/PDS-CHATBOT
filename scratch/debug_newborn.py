import io, sys, os

import traceback

from chatbot.router.router import route
from chatbot.entities.extractor import EntityExtractor
from chatbot.workflow.manager import WorkflowManager
from rag.retriever import retriever
from chatbot.services.rag_service import RAGService
class MockSession:
    def __init__(self, session_id):
        self.session_id = session_id
        self.current_intent = None
        self.entities = {}
        self.history = []
        self.user_context = {}

# Initialize retriever (loads ChromaDB)
retriever.initialize()

QUERIES = {
    "Failing": ["how to add the name of new born in ration card"],
    "Working": [
        "How can I update my ration card?",
        "How do I add a family member to my ration card?",
        "How can I add a child's name to my ration card?"
    ],
    "Variants": [
        "how to add the name of new born in ration card",
        "how to add newborn child in ration card",
        "how to add a newborn baby's name to ration card",
        "how to add new family member in ration card",
        "how to add child's name in ration card",
        "I had a baby, how do I add the baby to my ration card?"
    ]
}

def trace_query(q):
    print(f"\n{'='*80}\nQUERY: {q}\n{'='*80}")
    try:
        route_res = route(q)
        intent = route_res.intent
        print(f"[1. ROUTER] Intent: {intent} (conf: {route_res.confidence})")

        entities = EntityExtractor.extract(q, intent)
        ent_dict = {e.entity_type: e.value for e in entities}
        print(f"[2. ENTITIES] Extracted: {ent_dict}")

        session = MockSession(session_id="debug_123")
        session.current_intent = intent
        session.entities = ent_dict
        
        is_wf_complete = WorkflowManager.is_complete(session)
        print(f"[3. WORKFLOW] Is complete? {is_wf_complete}")
        
        # Try manually retrieving docs
        retrieval_res = retriever.search(q, top_k=5, intent=intent, state=ent_dict.get("states"), card_type=ent_dict.get("card_types"))
        docs = retrieval_res.get("documents", [[]])[0]
        metas = retrieval_res.get("metadatas", [[]])[0]
        print(f"[4. RETRIEVER] Count: {len(docs)}, Level: {retrieval_res.get('retrieval_level')}")
        for i, m in enumerate(metas):
            print(f"  - Doc {i+1}: {m.get('title')} | {m.get('intent')}")

        print(f"[5. RAG / GEMINI]")
        session.current_intent = intent
        session.entities = ent_dict
        rag = RAGService()
        
        # Override print to capture traceback inside RAG if any
        reply = rag.generate_response(session, q)
        if reply == "I apologize, but our AI service is currently experiencing technical difficulties. Please check the official PDS portal.":
            print("[GEMINI] RETURNED GENERIC ERROR MESSAGE!")
        else:
            print(f"[GEMINI] SUCCESS. Reply length: {len(reply)}")

    except Exception as e:
        print(f"[PIPELINE ERROR] {type(e).__name__}: {str(e)}")

for category, queries in QUERIES.items():
    print(f"\n\n{'#'*80}\nCATEGORY: {category}\n{'#'*80}")
    for q in queries:
        trace_query(q)
