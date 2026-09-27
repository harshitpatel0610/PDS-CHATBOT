from chatbot.router.service import RoutingService
from chatbot.entities.extractor import EntityExtractor
from rag.retriever import retriever
import json

# Temporarily patch ENTITY_CONFIG in memory so we can extract everything to see what HAPPENS if we fix it.
# Actually let's not patch it first, let's see the exact failure.
import chatbot.entities.extractor
# Add 'documents_required' and others to extractor config for the trace
chatbot.entities.extractor.ENTITY_CONFIG["documents_required"] = ["states", "card_types", "districts"]
chatbot.entities.extractor.ENTITY_CONFIG["ration_card_eligibility"] = ["states", "card_types", "districts"]
chatbot.entities.extractor.ENTITY_CONFIG["ration_card_types"] = ["states", "card_types", "districts"]
chatbot.entities.extractor.ENTITY_CONFIG["ration_card_online_offline"] = ["states", "card_types", "districts"]

def trace(query):
    print("="*80)
    print(f"QUERY: {query}")
    
    # 1. Routing
    routing_result = RoutingService.classify(query)
    intent = routing_result.intent
    print(f"INTENT: {intent}")
    
    # 2. Entity extraction
    entity_objs = EntityExtractor.extract(query, intent)
    entities = {e.entity_type: e.value for e in entity_objs}
    print(f"ENTITIES: {entities}")
    state = entities.get("states")
    card_type = entities.get("card_types")
    
    # 3. Retrieval
    res = retriever.search(query=query, top_k=3, intent=intent, state=state, card_type=card_type)
    print(f"RETRIEVAL LEVEL: {res.get('retrieval_level')}")
    
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    print(f"TOTAL DOCS RETRIEVED: {len(docs)}")
    for i, (doc, meta) in enumerate(zip(docs, metas)):
        print(f"\n--- Result {i+1} ---")
        print(f"Meta: {meta}")
        print(f"Doc snippet: {doc[:200]}...")
        
trace("What documents are required for an APL ration card in Gujarat?")
trace("What documents are required for BPL ration card in Karnataka?")
trace("Who is eligible for APL in Gujarat?")
trace("How do I apply for ration card in Karnataka?")
