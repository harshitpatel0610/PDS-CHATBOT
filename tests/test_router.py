from chatbot.router.router import route

test_queries = [
    "How do I apply for a ration card?",
    "I lost my ration card.",
    "How can I add my wife to the ration card?",
    "Complete my eKYC.",
    "What is the price of rice?",
    "Where is the nearest fair price shop?",
    "How do I file a complaint?",
    "Can I use my ration card in another state?",
    "Show my transaction history.",
    "Who is Virat Kohli?",
    "What is the capital of Japan?",
    "Tell me a joke."
]

for query in test_queries:
    result = route(query)

    print("=" * 60)
    print("Query      :", query)
    print("Is PDS     :", result.is_pds)
    print("Intent     :", result.intent)
    print("Confidence :", round(result.confidence, 2))
    print("\nEntities:")

    if result.entities:
        for entity in result.entities:
            print(
                f"- {entity.entity_type}: {entity.value} ({entity.confidence:.2f})"
            )
    else:
        print("No entities found.")