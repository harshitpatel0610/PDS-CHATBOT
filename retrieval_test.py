import json
from chatbot.services.chat_service import ChatService
from chatbot.conversation.session import ConversationSession
from rag.retriever import retriever
import os

queries = [
    "How can I apply for a new ration card?",
    "How can I apply for an APL ration card in Gujarat?",
    "How can I apply for an APL ration card in Sabarkantha, Gujarat?",
    "Can I apply for a ration card online?",
    "Can I apply for a ration card offline?",
    "Where can I add a family member to my ration card?",
    "How do I download my ration card?"
]

print("Running retrieval tests...\n")
for q in queries:
    print(f"{'='*80}\nQuery: {q}")
    session = ConversationSession("test")
    
    # Run the chat service to get intent and entities
    res = ChatService.process(session, q)
    intent = session.current_intent
    entities = session.entities
    
    print(f"Intent: {intent}")
    print(f"Entities: {json.dumps(entities)}")
    
    state = entities.get("states")
    district = entities.get("districts")
    card_type = entities.get("card_types")
    
    try:
        ret_res = retriever.search(
            query=q,
            top_k=5,
            intent=intent,
            state=state,
            
            card_type=card_type
        )
        
        print(f"Retrieval Level: {ret_res.get('retrieval_level')}")
        print(f"Top retrieved IDs: {ret_res.get('ids', [[]])[0]}")
        print(f"Distances: {ret_res.get('distances', [[]])[0]}")
        
        metas = ret_res.get('metadatas', [[]])[0]
        if metas:
            print(f"Metadata (Top 1): {json.dumps(metas[0])}")
        else:
            print("Metadata (Top 1): None")
            
    except Exception as e:
        print(f"Retrieval error: {e}")
    print()
