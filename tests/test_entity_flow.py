from chatbot.entities.extractor import EntityExtractor

def test_extractor():
    queries = [
        "Gujarat",
        "Sabarkantha",
        "Ahmedabad",
        "Surat"
    ]
    
    for q in queries:
        print(f"\n--- Testing: '{q}' ---")
        result = EntityExtractor.extract(q, "ration_card_apply")
        for ent in result:
            print(f"Type: {ent.entity_type}, Value: {ent.value}, Confidence: {ent.confidence}")

if __name__ == "__main__":
    test_extractor()
