from chatbot.entities.matcher import EntityMatcher


TESTS = [
    ("Karnataka", "states"),
    ("West Bengal", "states"),
    ("Tamil Nadu", "states"),
    ("Andhra Pradesh", "states"),
    ("Arunachal Pradesh", "states"),
    ("Andaman and Nicobar Islands", "states"),

    (
        "I want an AAY ration card in Karnataka",
        "states"
    ),

    (
        "I need a BPL ration card in West Bengal",
        "states"
    ),

    (
        "Can I apply for a ration card in Andhra Pradesh?",
        "states"
    ),

    (
        "I live in Arunachal Pradesh",
        "states"
    ),

    (
        "I live in Andaman and Nicobar Islands",
        "states"
    ),
]

FUZZY_TESTS = [
    ("Karnatka", "states"),
    ("Keral", "states"),
    ("Tamilnadu", "states"),
    ("West Bengl", "states"),
    ("Andra Pradesh", "states"),
    ("Arunachal Pardesh", "states"),

    ("BPL", "card_types"),
    ("AAY", "card_types"),
    ("APL", "card_types"),

    ("ricee", "commodities"),
    ("wheatt", "commodities"),
    ("kerosene", "commodities"),
]

AMBIGUOUS_TESTS = [
    ("Karn", "states"),
    ("Keral", "states"),
    ("Karnat", "states"),
    ("Andra", "states"),
    ("Pradesh", "states"),

    ("rice", "commodities"),
    ("ric", "commodities"),
    ("whea", "commodities"),
    ("wht", "commodities"),

    ("randomword", "states"),
    ("ration", "states"),
    ("India", "states"),
]


print("\n\n" + "=" * 70)
print("AMBIGUOUS / SHORT INPUT TESTS")
print("=" * 70)

for query, entity_type in AMBIGUOUS_TESTS:

    print("\nQuery:", query)
    print("Entity type:", entity_type)

    result = EntityMatcher.find(
        query,
        entity_type
    )

    print("Top 5:", result[:5])
    print("-" * 60)
    
'''
for query, entity_type in FUZZY_TESTS:

    print("\nQuery:", query)
    print("Entity type:", entity_type)

    result = EntityMatcher.find(
        query,
        entity_type
    )

    print("Result:", result)

    print("-" * 60)'''