from rag.retriever import retriever

def run_test(name, query, intent, state, district, card_type):
    print("="*60)
    print(f"TEST: {name}")
    print(f"Query: {query}")
    print(f"Intent: {intent}, State: {state}, District: {district}, Card Type: {card_type}")
    
    result = retriever.search(
        query=query,
        top_k=5,
        intent=intent,
        state=state,
        
        card_type=card_type
    )
    
    level = result.get("retrieval_level", "unknown")
    ids = result.get("ids", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]
    
    print(f"Retrieval Level: {level}")
    print(f"Retrieved IDs: {ids}")
    print(f"Distances: {distances}")
    for i, meta in enumerate(metadatas):
        print(f"Metadata {i}: {meta}")
    
    docs = result.get("documents", [[]])[0]
    print(f"Context Length: {len(docs)}")
    if docs:
        print(f"Final Context Sample: {docs[0][:100]}...")


if __name__ == "__main__":
    run_test(
        "TEST 1: Full specific",
        "How can I apply for an APL ration card in Sabarkantha, Gujarat?",
        "ration_card_apply", "Gujarat", "Sabarkantha", "APL"
    )

    run_test(
        "TEST 2: State only",
        "How do I apply for a ration card in Gujarat?",
        "ration_card_apply", "Gujarat", None, None
    )

    run_test(
        "TEST 3: Generic",
        "How do I apply for a ration card?",
        "ration_card_apply", None, None, None
    )

    run_test(
        "TEST 4: BPL specific",
        "How can I apply for a BPL ration card in Sabarkantha?",
        "ration_card_apply", "Gujarat", "Sabarkantha", "BPL"
    )

    run_test(
        "TEST 5: Nonexistent district",
        "How do I apply for an APL ration card in Nonexistent, Gujarat?",
        "ration_card_apply", "Gujarat", "Nonexistent", "APL"
    )
