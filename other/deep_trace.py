import re
from rapidfuzz import fuzz
from chatbot.router.rules import (
    normalize, is_online_offline_query, PDS_INTENTS,
    STRONG_ACTION_PHRASES, ONLINE_OFFLINE_SIGNALS
)
from chatbot.router.service import RoutingService, RULE_CONFIDENCE_THRESHOLD

queries = [
    "Can I apply online without Aadhaar?",
    "Who is eligible and can they apply online?",
    "How can I apply for APL?",
    "What documents are required to apply for APL ration card?",
    "Who is the ration card officer?",
    "Can I update my Aadhaar document after applying?",
    "Where can I submit my documents?",
    "How do I upload documents online?",
    "What happens after document verification?",
    "How can an eligible person apply?",
    "What documents should an eligible applicant submit?",
    "APL ke liye kon apply kar sakta hai?",
    "Aadhar nhi hai to apply kar skte hai?",
]

for q in queries:
    nq = normalize(q)
    is_oo = is_online_offline_query(nq)
    
    # Simulate scoring loop
    best_intent = None
    best_score = 0.0
    top3 = []
    for intent in PDS_INTENTS:
        score = 0.0
        intent_name = intent["intent"]
        for keyword in intent.get("keywords", []):
            keyword = normalize(keyword)
            if not keyword:
                continue
            if keyword in nq:
                if len(keyword) <= 3:
                    score += 10
                elif len(keyword.split()) >= 3:
                    score += 40
                elif len(keyword.split()) == 2:
                    score += 30
                else:
                    score += 20
        for pattern in intent.get("patterns", []):
            pattern = normalize(pattern)
            if not pattern:
                continue
            similarity = max(fuzz.partial_ratio(nq, pattern), fuzz.token_set_ratio(nq, pattern))
            pattern_score = similarity * 0.4
            if pattern_score > score:
                score = pattern_score
        for example in intent.get("examples", []):
            example = normalize(example)
            if not example:
                continue
            similarity = fuzz.token_set_ratio(nq, example)
            example_score = similarity * 0.4
            if example_score > score:
                score = example_score
        for negative in intent.get("negative_patterns", []):
            negative = normalize(negative)
            if negative and negative in nq:
                score -= 30
        for phrase in STRONG_ACTION_PHRASES.get(intent_name, []):
            phrase = normalize(phrase)
            if phrase in nq:
                score += 50
                break
        score += intent.get("priority", 0)
        top3.append((intent_name, score))
        if score > best_score:
            best_score = score
            best_intent = intent
    
    top3.sort(key=lambda x: -x[1])
    conf = min(best_score / 100, 1.0)
    
    # Get final classify result
    result = RoutingService.classify(q)
    
    print(f"\n{'='*70}")
    print(f"QUERY: {q}")
    print(f"  normalized: {nq}")
    print(f"  is_online_offline: {is_oo}")
    if is_oo:
        print(f"  ** EARLY RETURN: ration_card_online_offline @ 1.0 **")
    print(f"  rule_best: {best_intent['intent'] if best_intent else None} @ score={best_score:.1f} conf={conf:.4f}")
    print(f"  top3_scores: {top3[:5]}")
    print(f"  rule_conf >= threshold? {conf >= RULE_CONFIDENCE_THRESHOLD}")
    print(f"  FINAL: intent={result.intent} conf={result.confidence:.4f}")
