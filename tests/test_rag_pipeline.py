from rag.retriever import retriever
from chatbot.entities.extractor import EntityExtractor

def test_rag():
    retriever.initialize()
    
    # Test 1: Cross-state contamination (Karnataka query shouldn't return Gujarat data)
    query1 = "How do I apply for ration card in Karnataka?"
    intent1 = "ration_card_apply"
    entities1 = EntityExtractor.extract(query1, intent1)
    state1 = next((e.value for e in entities1 if e.entity_type == "states"), None)
    
    assert state1 == "Karnataka", f"Failed to extract state. Got {state1}"
    
    results1 = retriever.search(query1, top_k=5, intent=intent1, state=state1)
    for meta in results1["metadatas"][0]:
        assert meta.get("state") in ["Karnataka", "Generic"], f"Cross-state contamination! Found {meta.get('state')} document for Karnataka query."
        
    print("PASS: Cross-state contamination prevented.")
    
    # Test 2: Intent restriction (documents_required shouldn't return apply docs if we fix extraction)
    query2 = "What documents are required for an APL ration card in Gujarat?"
    intent2 = "documents_required"
    entities2 = EntityExtractor.extract(query2, intent2)
    state2 = next((e.value for e in entities2 if e.entity_type == "states"), None)
    card_type2 = next((e.value for e in entities2 if e.entity_type == "card_types"), None)
    
    assert state2 == "Gujarat", "Failed to extract Gujarat"
    assert card_type2 == "APL", "Failed to extract APL"
    
    results2 = retriever.search(query2, top_k=5, intent=intent2, state=state2, card_type=card_type2)
    for meta in results2["metadatas"][0]:
        assert meta.get("intent") == "documents_required", f"Wrong intent returned: {meta.get('intent')}"
        assert meta.get("state") in ["Gujarat", "Generic"], f"Cross-state contamination! Found {meta.get('state')} document for Gujarat query."
        
    print("PASS: Intent and State restriction enforced.")

if __name__ == "__main__":
    test_rag()
