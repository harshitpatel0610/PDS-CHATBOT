from chatbot.entities.extractor import EntityExtractor


TESTS = [
    # ---------------------------------
    # STATE + CARD TYPE
    # ---------------------------------

    (
        "I want an AAY ration card in Karnataka",
        "ration_card_apply"
    ),

    (
        "I need a BPL ration card in West Bengal",
        "ration_card_apply"
    ),

    (
        "Can I apply for an APL ration card in Tamil Nadu?",
        "ration_card_apply"
    ),

    (
        "Mujhe Karnataka me AAY ration card apply karna hai",
        "ration_card_apply"
    ),

    # ---------------------------------
    # STATE + CARD TYPE + OTHER
    # ---------------------------------

    (
        "I want to apply for a BPL ration card in Kerala",
        "ration_card_apply"
    ),

    (
        "Can I get an AAY card in Bihar?",
        "ration_card_apply"
    ),

    # ---------------------------------
    # FAMILY RELATION
    # ---------------------------------

    (
        "I want to add my wife to my ration card",
        "add_family_member"
    ),

    (
        "How can I add my brother to my ration card?",
        "add_family_member"
    ),

    (
        "I need to add my mother to my ration card",
        "add_family_member"
    ),

    (
        "Mujhe apni wife ka naam ration card me add karna hai",
        "add_family_member"
    ),

    # ---------------------------------
    # REMOVE FAMILY MEMBER
    # ---------------------------------

    (
        "I want to remove my daughter from my ration card",
        "remove_family_member"
    ),

    (
        "I need to remove my brother from the ration card",
        "remove_family_member"
    ),

    # ---------------------------------
    # COMMODITIES
    # ---------------------------------

    (
        "What is the price of rice?",
        "ration_price"
    ),

    (
        "What is the price of wheat in Karnataka?",
        "ration_price"
    ),

    (
        "How much does rice and wheat cost?",
        "ration_price"
    ),

    (
        "What commodities are available in Kerala?",
        "ration_items_list"
    ),

    # ---------------------------------
    # MIXED ENTITIES
    # ---------------------------------

    (
        "I need rice in Karnataka",
        "ration_items_list"
    ),

    (
        "I want wheat and rice in Kerala",
        "ration_items_list"
    ),

    (
        "Can I get AAY ration in Karnataka?",
        "ration_card_apply"
    ),

    (
        "I want a BPL card and I live in Tamil Nadu",
        "ration_card_apply"
    ),
]


for query, intent in TESTS:

    print("\n" + "=" * 70)

    print("QUERY:")
    print(query)

    print("\nINTENT:")
    print(intent)

    print("\nEXTRACTED ENTITIES:")

    entities = EntityExtractor.extract(
        query,
        intent
    )

    if not entities:
        print("NO ENTITIES FOUND")
        continue

    for entity in entities:

        print(
            f"Type       : {entity.entity_type}"
        )

        print(
            f"Value      : {entity.value}"
        )

        print(
            f"Confidence : {entity.confidence:.2f}"
        )