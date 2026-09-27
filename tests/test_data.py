import json

from chatbot.router.router import route
from chatbot.entities.extractor import EntityExtractor


# ============================================================
# LOAD TEST CASES
# ============================================================

with open("test_cases.json", "r", encoding="utf-8") as file:
    test_cases = json.load(file)


# ============================================================
# COUNTERS
# ============================================================

total = 0
passed = 0
failed = 0

failed_cases = []


# ============================================================
# HEADER
# ============================================================

print("=" * 100)
print("PDS AI ASSISTANT - AUTOMATED TEST SUITE")
print("=" * 100)


# ============================================================
# RUN TESTS
# ============================================================

for test in test_cases:

    total += 1

    query = test["query"]

    expected_intent = test.get("expected_intent")
    expected_entity_type = test.get("expected_entity_type")
    expected_entity = test.get("expected_entity")


    # ========================================================
    # INTENT TEST
    # ========================================================

    if expected_intent is not None:

        result = route(query)

        actual_intent = result.intent

        if actual_intent == expected_intent:

            passed += 1

            print(
                f"PASS | {query}"
            )

        else:

            failed += 1

            print(
                f"FAIL | {query}"
            )

            print(
                f"      Expected   : {expected_intent}"
            )

            print(
                f"      Predicted  : {actual_intent}"
            )

            print(
                f"      Confidence : {result.confidence:.3f}"
            )

            failed_cases.append({
                "query": query,
                "expected": expected_intent,
                "predicted": actual_intent,
                "confidence": result.confidence
            })


    # ========================================================
    # NON-PDS TEST
    # ========================================================

    elif (
        expected_intent is None
        and "expected_entity_type" not in test
    ):

        result = route(query)

        if not result.is_pds:

            passed += 1

            print(
                f"PASS | {query}"
            )

        else:

            failed += 1

            print(
                f"FAIL | {query}"
            )

            print(
                f"      Expected   : Non-PDS"
            )

            print(
                f"      Predicted  : {result.intent}"
            )

            print(
                f"      Confidence : {result.confidence:.3f}"
            )

            failed_cases.append({
                "query": query,
                "expected": "Non-PDS",
                "predicted": result.intent,
                "confidence": result.confidence
            })


    # ========================================================
    # ENTITY TEST
    # ========================================================

    elif expected_entity_type is not None:

        entities = EntityExtractor.extract(
            query,
            "ration_card_apply"
        )

        found = False

        for entity in entities:

            if (
                entity.entity_type == expected_entity_type
                and entity.value == expected_entity
            ):
                found = True
                break


        if found:

            passed += 1

            print(
                f"PASS | {query}"
            )

        else:

            failed += 1

            print(
                f"FAIL | {query}"
            )

            print(
                f"      Expected   : "
                f"{expected_entity_type} = {expected_entity}"
            )

            print(
                f"      Found      : {entities}"
            )

            failed_cases.append({
                "query": query,
                "expected": (
                    f"{expected_entity_type} = "
                    f"{expected_entity}"
                ),
                "predicted": str(entities),
                "confidence": None
            })


# ============================================================
# CALCULATE RESULTS
# ============================================================

passed_percentage = (
    (passed / total) * 100
    if total > 0
    else 0
)

failed_percentage = (
    (failed / total) * 100
    if total > 0
    else 0
)

accuracy = passed_percentage


# ============================================================
# FINAL RESULTS
# ============================================================

print()
print()
print("=" * 100)
print("TEST RESULTS")
print("=" * 100)

print()

print(f"Total Queries : {total}")

print(
    f"Passed        : {passed} "
    f"({passed_percentage:.2f}%)"
)

print(
    f"Failed        : {failed} "
    f"({failed_percentage:.2f}%)"
)

print(
    f"Accuracy      : {accuracy:.2f}%"
)


# ============================================================
# FAILED QUERY SUMMARY
# ============================================================

if failed_cases:

    print()
    print("=" * 100)
    print("FAILED QUERIES")
    print("=" * 100)

    for index, case in enumerate(failed_cases, 1):

        print()
        print(f"{index}. Query      : {case['query']}")
        print(f"   Expected     : {case['expected']}")
        print(f"   Predicted    : {case['predicted']}")

        if case["confidence"] is not None:

            print(
                f"   Confidence   : "
                f"{case['confidence']:.3f}"
            )


# ============================================================
# ALL PASSED
# ============================================================

else:

    print()
    print("=" * 100)
    print("ALL TESTS PASSED")
    print("=" * 100)