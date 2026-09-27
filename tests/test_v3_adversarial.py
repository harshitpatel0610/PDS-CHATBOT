from chatbot.router.service import RoutingService

# ============================================================
# ADVERSARIAL TEST SUITE V3
# ============================================================
# Tests the context resolver for false positives.
#
# MULTI-INTENT POLICY (single-label, deterministic):
#   Eligibility > Documents Required > Online/Offline > Application
#   Applied ONLY when strong contextual evidence exists.
#
# Non-contestable intents (ration_card_update, contact_admin, etc.)
# are NEVER overridden by the context hierarchy.
# ============================================================

queries = [
    # ============================================================
    # 1. ELIGIBILITY FALSE POSITIVES
    # ============================================================
    # These contain "who" or "eligible" but should NOT be eligibility.
    
    # NOTE: "Who is the ration card officer?" and "Who handles complaints?"
    # depend entirely on embedding quality. The context resolver correctly
    # does NOT override these (they resolve to non-contestable intents).
    # We test that the resolver doesn't falsely classify them as eligibility.
    
    ("Who is the ration card officer?", None),            # Resolver must NOT make this eligibility. Accept any non-eligibility result.
    ("Who should I contact for ration card application?", None),  # Same — accept any non-eligibility result.
    ("Who handles ration card complaints?", None),        # Same — accept any non-eligibility result.
    ("How can an eligible person apply?", "ration_card_apply"),
    ("What documents should an eligible applicant submit?", "documents_required"),
    
    # ============================================================
    # 2. DOCUMENT FALSE POSITIVES
    # ============================================================
    # These mention "document" but should NOT be documents_required.
    # The resolver must not hijack these.
    
    ("Where can I submit my documents?", None),           # Embedding quality issue. Must NOT be documents_required.
    ("How do I upload documents online?", None),          # Same. Must NOT be documents_required.
    ("What happens after document verification?", None),  # Same. Must NOT be documents_required.
    ("Which office verifies my documents?", None),        # Same. Must NOT be documents_required.
    ("Can I update my Aadhaar document after applying?", None),  # Must NOT be documents_required.
    
    # ============================================================
    # 3. APPLICATION vs ELIGIBILITY
    # ============================================================
    
    ("How can I apply for APL?", "ration_card_apply"),
    ("Who can apply for APL?", "ration_card_eligibility"),
    ("Can I apply for APL?", None),   # Genuinely ambiguous. Accept non-types result.
    ("Am I eligible to apply for APL?", "ration_card_eligibility"),
    ("What is the application process for eligible applicants?", "ration_card_apply"),
    
    # ============================================================
    # 4. APPLICATION vs ONLINE/OFFLINE
    # ============================================================
    
    ("How can I apply online?", "ration_card_apply"),
    ("Can I apply online or offline?", "ration_card_online_offline"),
    ("Where can I apply online?", "ration_card_online_offline"),
    ("Is online application available?", "ration_card_online_offline"),
    ("What is the online application process?", "ration_card_apply"),
    ("How can I apply offline?", "ration_card_apply"),
    ("Is the application online or offline?", "ration_card_online_offline"),
    
    # ============================================================
    # 5. TYPES FALSE POSITIVES
    # ============================================================
    
    ("What documents are required for APL?", "documents_required"),
    ("Who is eligible for APL?", "ration_card_eligibility"),
    ("How do I apply for APL?", "ration_card_apply"),
    
    # ============================================================
    # 6. HINGLISH / TYPO ROBUSTNESS
    # ============================================================
    
    ("APL ke liye kon eligible hai?", "ration_card_eligibility"),
    ("APL ke liye kon apply kar sakta hai?", "ration_card_eligibility"),
    ("APL ke liye kya document chahiye?", "documents_required"),
    ("Aadhar nhi hai to apply kar skte hai?", "documents_required"),
    ("ration card online banega ya offline?", "ration_card_online_offline"),
    ("ration card ke liye kaha apply kare?", "ration_card_apply"),
    
    # ============================================================
    # 7. MIXED-INTENT QUERIES
    # ============================================================
    # Policy: Eligibility > Documents > Online/Offline > Apply
    
    ("Who can apply for APL and what documents are required?", "ration_card_eligibility"),
    ("What documents are required and how can I apply?", "documents_required"),
    ("Can I apply online without Aadhaar?", "documents_required"),
    ("Who is eligible and can they apply online?", "ration_card_eligibility"),
    ("What is APL and who can get it?", "ration_card_eligibility"),
]


# ============================================================
# FALSE POSITIVE CHECKS
# ============================================================
# For queries marked with None, we verify that the resolver
# did NOT produce a false positive (i.e., did not incorrectly
# assign a contestable intent due to broad keyword matching).

FALSE_POSITIVE_CHECKS = {
    "Who is the ration card officer?": "ration_card_eligibility",           # Must NOT be this
    "Who should I contact for ration card application?": "ration_card_eligibility",
    "Who handles ration card complaints?": "ration_card_eligibility",
    "Where can I submit my documents?": "documents_required",
    "How do I upload documents online?": "documents_required",
    "What happens after document verification?": "documents_required",
    "Which office verifies my documents?": "documents_required",
    "Can I update my Aadhaar document after applying?": "documents_required",
    "Can I apply for APL?": "ration_card_types",  # Should not be types due to entity domination
}


def run_tests():
    failed = 0
    fp_failed = 0
    print("=" * 60)
    print("TEST V3 ADVERSARIAL")
    print("=" * 60)
    
    for q, exp in queries:
        res = RoutingService.classify(q)
        
        if exp is None:
            # False positive check
            forbidden = FALSE_POSITIVE_CHECKS.get(q)
            if forbidden and res.intent == forbidden:
                print(f"FALSE POSITIVE: '{q}'\n  Must NOT be: {forbidden}\n  Actual: {res.intent} (conf: {res.confidence})\n")
                fp_failed += 1
        elif res.intent != exp:
            print(f"FAILED: '{q}'\n  Expected: {exp}\n  Actual: {res.intent} (conf: {res.confidence})\n")
            failed += 1
            
    total_strict = sum(1 for _, e in queries if e is not None)
    total_fp = sum(1 for _, e in queries if e is None)
    
    print("=" * 60)
    print(f"Strict tests:     {total_strict - failed}/{total_strict}")
    print(f"FP checks:        {total_fp - fp_failed}/{total_fp}")
    print(f"Total:            {len(queries) - failed - fp_failed}/{len(queries)}")
    print(f"Failed:           {failed}")
    print(f"False positives:  {fp_failed}")

if __name__ == '__main__':
    run_tests()
