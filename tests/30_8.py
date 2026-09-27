from chatbot.router.service import RoutingService


router = RoutingService()


TEST_QUERIES = [

    # ============================================================
    # A. DOCUMENT REQUIREMENT
    # ============================================================

    (
        "Can I get a ration card without Aadhaar?",
        "documents_required",
    ),
    (
        "I don't have Aadhaar, can I apply for ration card?",
        "documents_required",
    ),
    (
        "I do not have Aadhaar card, can I get ration card?",
        "documents_required",
    ),
    (
        "Aadhaar nahi hai, ration card ban sakta hai?",
        "documents_required",
    ),
    (
        "Aadhaar nahi hai to ration card ke liye apply kar sakte hai?",
        "documents_required",
    ),
    (
        "What happens if I don't have Aadhaar?",
        "documents_required",
    ),
    (
        "Is Aadhaar compulsory for APL ration card?",
        "documents_required",
    ),
    (
        "Is Aadhaar compulsory to apply for BPL ration card?",
        "documents_required",
    ),
    (
        "Which documents are compulsory for APL ration card?",
        "documents_required",
    ),
    (
        "What paperwork do I need for APL ration card?",
        "documents_required",
    ),
    (
        "What documents are required to apply for APL ration card?",
        "documents_required",
    ),
    (
        "Which proof is needed while applying for ration card?",
        "documents_required",
    ),

    # ============================================================
    # B. ELIGIBILITY
    # ============================================================

    (
        "Who is eligible for APL ration card?",
        "ration_card_eligibility",
    ),
    (
        "Who can get an APL ration card?",
        "ration_card_eligibility",
    ),
    (
        "Who qualifies for BPL ration card?",
        "ration_card_eligibility",
    ),
    (
        "Who is allowed to apply for BPL ration card?",
        "ration_card_eligibility",
    ),
    (
        "Can I qualify for APL ration card?",
        "ration_card_eligibility",
    ),
    (
        "What are the eligibility criteria for BPL ration card?",
        "ration_card_eligibility",
    ),
    (
        "Am I eligible for an APL ration card?",
        "ration_card_eligibility",
    ),
    (
        "What are the eligibility requirements for ration card?",
        "ration_card_eligibility",
    ),

    # ============================================================
    # C. APPLICATION
    # ============================================================

    (
        "How do I apply for APL ration card?",
        "ration_card_apply",
    ),
    (
        "Where do I apply for APL ration card?",
        "ration_card_apply",
    ),
    (
        "What is the application process for ration card?",
        "ration_card_apply",
    ),
    (
        "How can I submit my ration card application?",
        "ration_card_apply",
    ),
    (
        "Where can I submit the ration card application?",
        "ration_card_apply",
    ),
    (
        "How can I apply for a ration card online?",
        "ration_card_apply",
    ),
    (
        "APL ration card ke liye apply kaise kare?",
        "ration_card_apply",
    ),
    (
        "ration card ke liye application kaha karni hai?",
        "ration_card_apply",
    ),

    # ============================================================
    # D. TYPES
    # ============================================================

    (
        "What is APL?",
        "ration_card_types",
    ),
    (
        "What is BPL?",
        "ration_card_types",
    ),
    (
        "What are the different ration card categories?",
        "ration_card_types",
    ),
    (
        "Is APL different from BPL?",
        "ration_card_types",
    ),
    (
        "Which types of ration cards are available?",
        "ration_card_types",
    ),
    (
        "What are the different types of ration cards?",
        "ration_card_types",
    ),
    (
        "Is BPL a type of ration card?",
        "ration_card_types",
    ),

    # ============================================================
    # E. DELIBERATE COLLISIONS
    # ============================================================

    (
        "Who can apply for APL and what documents are required?",
        "ration_card_eligibility",
    ),
    (
        "Who is eligible to apply for APL ration card?",
        "ration_card_eligibility",
    ),
    (
        "Who can apply for BPL ration card and what is the process?",
        "ration_card_eligibility",
    ),
    (
        "Can an eligible person apply without Aadhaar?",
        "documents_required",
    ),
    (
        "How can I apply if I don't have Aadhaar?",
        "documents_required",
    ),
    (
        "What documents do I need before applying for APL?",
        "documents_required",
    ),
    (
        "I want to apply for APL but I don't have Aadhaar",
        "documents_required",
    ),
    (
        "Can I apply for APL ration card without Aadhaar?",
        "documents_required",
    ),
]


def extract_intent(result):
    """
    Supports common response formats.
    If your RoutingService returns a custom object,
    adjust this function accordingly.
    """

    if isinstance(result, dict):
        return (
            result.get("intent")
            or result.get("predicted_intent")
            or result.get("label")
        )

    return (
        getattr(result, "intent", None)
        or getattr(result, "predicted_intent", None)
        or getattr(result, "label", None)
    )


def extract_confidence(result):
    if isinstance(result, dict):
        return (
            result.get("confidence")
            or result.get("score")
            or result.get("probability")
        )

    return (
        getattr(result, "confidence", None)
        or getattr(result, "score", None)
        or getattr(result, "probability", None)
    )


def main():

    passed = 0
    failed = 0
    errors = 0

    failures = []

    print("=" * 100)
    print("                    PDS INTENT ROUTER - V2 COLLISION TEST")
    print("=" * 100)

    for index, (query, expected) in enumerate(TEST_QUERIES, start=1):

        try:
            result = router.classify(query)

            actual = extract_intent(result)
            confidence = extract_confidence(result)

            if actual == expected:
                passed += 1
                status = "PASS"
            else:
                failed += 1
                status = "FAIL"

                failures.append({
                    "query": query,
                    "expected": expected,
                    "actual": actual,
                    "confidence": confidence,
                })

            print(f"\n[{index:02d}] {status}")
            print(f"Query      : {query}")
            print(f"Expected   : {expected}")
            print(f"Actual     : {actual}")
            print(f"Confidence : {confidence}")

        except Exception as e:
            errors += 1

            print(f"\n[{index:02d}] ERROR")
            print(f"Query      : {query}")
            print(f"Expected   : {expected}")
            print(f"Error      : {e}")

    total = len(TEST_QUERIES)

    print("\n" + "=" * 100)
    print("                         TEST SUMMARY")
    print("=" * 100)

    print(f"Total      : {total}")
    print(f"Passed     : {passed}")
    print(f"Failed     : {failed}")
    print(f"Errors     : {errors}")

    if total:
        accuracy = (passed / total) * 100
        print(f"Accuracy   : {accuracy:.2f}%")

    print("=" * 100)

    if failures:

        print("\nFAILED CASES")
        print("-" * 100)

        for i, failure in enumerate(failures, start=1):

            print(f"\nFailure #{i}")
            print(f"Query      : {failure['query']}")
            print(f"Expected   : {failure['expected']}")
            print(f"Actual     : {failure['actual']}")
            print(f"Confidence : {failure['confidence']}")

    else:
        print("\nAll V2 collision tests passed! 🎯")


if __name__ == "__main__":
    main()