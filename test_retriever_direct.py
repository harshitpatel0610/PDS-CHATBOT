from rag.retriever import retriever

def test_retriever():
    print("--- Test 1 ---")
    res1 = retriever.search(
        "How can I apply for a new ration card?",
        top_k=5,
        intent="ration_card_apply"
    )
    print("IDs:", res1.get("ids", [[]])[0])
    print("Distances:", res1.get("distances", [[]])[0])
    print("Metadata:", res1.get("metadatas", [[]])[0])
    print("Documents Count:", len(res1.get("documents", [[]])[0]))

    print("\n--- Test 2 ---")
    res2 = retriever.search(
        "How can I apply for a new ration card in Gujarat, Sabarkantha for APL?",
        top_k=5,
        intent="ration_card_apply"
    )
    print("IDs:", res2.get("ids", [[]])[0])
    print("Distances:", res2.get("distances", [[]])[0])
    print("Metadata:", res2.get("metadatas", [[]])[0])
    print("Documents Count:", len(res2.get("documents", [[]])[0]))

if __name__ == "__main__":
    test_retriever()
