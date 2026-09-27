"""
RAG Retrieval Evaluation
========================

Run from project root:

    python tests/test_retrieval.py

Evaluates:
- Top-1 Accuracy
- Top-3 Recall
- Top-5 Recall
- Mean Reciprocal Rank (MRR)

Also prints failed queries and saves:
    tests/retrieval_results.csv
"""

from pathlib import Path
import csv
import sys
import time


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Allows:
# from rag.retriever import retriever
sys.path.insert(0, str(PROJECT_ROOT))

from rag.retriever import retriever
from chatbot.router.router import route


# ============================================================
# TEST DATA
# ============================================================

TEST_CASES = [

    # --------------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------------

    ("How do I log in as an admin?", "admin_login"),
    ("Admin login is not working", "admin_login"),

    ("How does a customer log in?", "customer_login"),
    ("I cannot log into my customer account", "customer_login"),

    ("How do I log in as a distributor?", "distributor_login"),
    ("I am not able to log in", "login_not_working"),

    ("I did not receive my OTP", "otp_issue"),
    ("The OTP is not coming to my phone", "otp_issue"),

    ("How can I find my customer ID?", "customer_id_inquiry"),
    ("Where can I find my distributor ID?", "distributor_id_inquiry"),


    # --------------------------------------------------------
    # AADHAAR / ACCOUNT MANAGEMENT
    # --------------------------------------------------------

    ("How do I link Aadhaar to my ration card?", "aadhaar_linking"),
    ("I want to update my address", "update_address"),
    ("How can I change my registered mobile number?", "update_phone_number"),
    ("I need to change my profile photo", "update_photo"),
    ("Can I update my ration data?", "ration_data_privacy"),


    # --------------------------------------------------------
    # BENEFICIARY
    # --------------------------------------------------------

    ("How is a beneficiary verified?", "beneficiary_verification"),
    ("How do I verify a beneficiary?", "beneficiary_verification"),


    # --------------------------------------------------------
    # COMPLAINTS
    # --------------------------------------------------------

    ("How can I file a complaint?", "file_complaint"),
    ("I want to register a complaint", "file_complaint"),

    ("What types of complaints can I make?", "complaint_types"),

    ("What is the eligibility for filing a complaint?",
     "complaint_eligibility"),

    ("How are complaints resolved?", "complaint_resolution"),

    ("How can I check my complaint status?", "complaint_status"),
    ("What is the status of my complaint?", "complaint_status"),


    # --------------------------------------------------------
    # GRIEVANCE ESCALATION
    # --------------------------------------------------------

    ("How do I complain about black marketing?",
     "black_market_complaint"),

    ("My dealer is behaving badly",
     "dealer_misconduct"),

    ("The ration dealer is overcharging me",
     "overcharging_complaint"),

    ("The quality of ration is poor",
     "quality_complaint"),


    # --------------------------------------------------------
    # ADMIN
    # --------------------------------------------------------

    ("How does an admin manage complaints?",
     "admin_complaint_management"),

    ("How can an admin manage customers?",
     "admin_customer_management"),

    ("How can an admin manage distributors?",
     "admin_distributor_management"),

    ("How can an admin generate system reports?",
     "admin_system_reports"),

    ("What reports are available to an administrator?",
     "admin_system_reports"),


    # --------------------------------------------------------
    # DISTRIBUTOR
    # --------------------------------------------------------

    ("How can a distributor view customers?",
     "distributor_customer_list"),

    ("How does distributor OTP verification work?",
     "distributor_otp_verification"),

    ("How can a distributor view their profile?",
     "distributor_profile"),

    ("How can a distributor generate a report?",
     "distributor_report"),

    ("How does a distributor manage stock?",
     "distributor_stock"),

    ("How can a distributor record ration distribution?",
     "record_distribution"),


    # --------------------------------------------------------
    # DOCUMENTS
    # --------------------------------------------------------

    ("What documents are required for a ration card?",
     "documents_required"),

    ("Which documents do I need to submit?",
     "documents_required"),

    ("What is an income certificate?",
     "income_certificate"),

    ("Why do I need an income certificate?",
     "income_certificate"),


    # --------------------------------------------------------
    # FAMILY MANAGEMENT
    # --------------------------------------------------------

    ("How do I add a family member?",
     "add_family_member"),

    ("How do I remove a family member?",
     "remove_family_member"),

    ("How do I remove a deceased family member?",
     "death_member_removal"),

    ("How can I view my family details?",
     "family_details_view"),

    ("How can I change the family head?",
     "family_head_change"),

    ("How do I register a newborn family member?",
     "new_born_registration"),


    # --------------------------------------------------------
    # GENERAL HELP
    # --------------------------------------------------------

    ("How can I contact the administrator?",
     "contact_admin"),

    ("I want to give feedback",
     "feedback"),

    ("Goodbye",
     "goodbye"),

    ("Hello",
     "greeting"),

    ("Hi",
     "greeting"),

    ("I need help with the PDS system",
     "help_request"),

    ("What is the PDS helpline?",
     "pds_helpline"),


    # --------------------------------------------------------
    # HISTORY
    # --------------------------------------------------------

    ("How can I see my transaction history?",
     "transaction_history"),

    ("Show me my previous ration transactions",
     "transaction_history"),


    # --------------------------------------------------------
    # PORTABILITY
    # --------------------------------------------------------

    ("Can migrants use their ration card in another state?",
     "migrant_ration"),

    ("Can I get ration outside my home state?",
     "migrant_ration"),


    # --------------------------------------------------------
    # PORTAL NAVIGATION
    # --------------------------------------------------------

    ("Does the PDS portal support different languages?",
     "language_support"),

    ("Can I access PDS services on mobile?",
     "mobile_access"),

    ("What is the PDS portal?",
     "portal_overview"),

    ("The PDS portal is not working",
     "portal_technical_issue"),


    # --------------------------------------------------------
    # RATION CARD
    # --------------------------------------------------------

    ("Where do I apply for a ration card?",
     "ration_card_apply"),

    ("I want to get a new ration card",
     "ration_card_apply"),

    ("How can I apply for a ration card?",
     "ration_card_apply"),

    ("Can I apply for a ration card online?",
     "ration_card_online_offline"),

    ("Is ration card application available online?",
     "ration_card_online_offline"),

    ("How do I download my ration card?",
     "ration_card_download"),

    ("I lost my ration card, what can I do?",
     "ration_card_duplicate"),

    ("Who is eligible for a ration card?",
     "ration_card_eligibility"),

    ("Am I eligible for a ration card?",
     "ration_card_eligibility"),

    ("Where can I find my ration card number?",
     "ration_card_number_inquiry"),

    ("I forgot my ration card number",
     "ration_card_number_inquiry"),

    ("How can I check my ration card status?",
     "ration_card_status"),

    ("What is a smart ration card?",
     "smart_ration_card"),

    ("How do I surrender my ration card?",
     "ration_card_surrender"),

    ("How can I transfer my ration card?",
     "ration_card_transfer"),

    ("What types of ration cards are available?",
     "ration_card_types"),

    ("How do I update my ration card?",
     "ration_card_update"),

    ("How long does it take to get a ration card?",
     "ration_card_waiting_time"),


    # --------------------------------------------------------
    # RATION COLLECTION
    # --------------------------------------------------------

    ("How does the ration collection process work?",
     "ration_collection_process"),

    ("What is the status of my ration collection?",
     "ration_collection_status"),

    ("What is an ePOS machine?",
     "epos_machine"),

    ("What ration items are available?",
     "ration_items_list"),

    ("When can I collect my monthly ration?",
     "ration_month_schedule"),

    ("I did not receive my ration",
     "ration_not_received"),

    ("The ration was not given to me",
     "ration_not_received"),

    ("What is the price of ration?",
     "ration_price"),

    ("How much ration am I entitled to receive?",
     "ration_quota"),

    ("What is my monthly ration quota?",
     "ration_quota"),

    ("Where can I find my ration shop?",
     "ration_shop_location"),

    ("Where is my Fair Price Shop?",
     "ration_shop_location"),


    # --------------------------------------------------------
    # SCHEMES
    # --------------------------------------------------------

    ("What is Antyodaya Anna Yojana?",
     "antyodaya_anna_yojana"),

    ("What is NFSA eligibility?",
     "nfsa_eligibility"),

    ("What is One Nation One Ration Card?",
     "one_nation_one_ration_card"),

    ("What is PMGKAY?",
     "pmgkay_scheme"),
]


# ============================================================
# HELPER
# ============================================================

def get_intent(metadata):
    """
    Extract intent from Chroma metadata.

    Current ingestion stores:
        title
        category
        source

    It does NOT currently store intent.

    Therefore we first try metadata["intent"].
    If unavailable, we derive intent from the source filename.
    """

    if not metadata:
        return None

    if metadata.get("intent"):
        return metadata["intent"]

    source = metadata.get("source", "")

    if source:
        filename = Path(source).stem

        # ration_card files have short filenames but
        # descriptive intents.
        ration_card_mapping = {
            "apply": "ration_card_apply",
            "download": "ration_card_download",
            "duplicate": "ration_card_duplicate",
            "eligibility": "ration_card_eligibility",
            "number_inquiry": "ration_card_number_inquiry",
            "online_offline": "ration_card_online_offline",
            "status": "ration_card_status",
            "surrender": "ration_card_surrender",
            "transfer": "ration_card_transfer",
            "types": "ration_card_types",
            "update": "ration_card_update",
            "waiting_time": "ration_card_waiting_time",
        }

        if filename in ration_card_mapping:
            return ration_card_mapping[filename]

        return filename

    return None


# ============================================================
# EVALUATION
# ============================================================

def evaluate():

    total = len(TEST_CASES)

    top1_correct = 0
    top3_correct = 0
    top5_correct = 0

    reciprocal_ranks = []

    rows = []

    print("=" * 80)
    print("PDS RAG RETRIEVAL EVALUATION")
    print("=" * 80)

    print(f"Total test queries : {total}")
    print()

    start_time = time.perf_counter()

    for number, (query, expected_intent) in enumerate(
        TEST_CASES,
        start=1
    ):

        try:
            
            route_result = route(query)
            detected_intent = route_result.intent if route_result.is_pds else None

            result = retriever.search(
                query,
                top_k=5,
                intent=detected_intent
            )

            documents = result.get(
                "documents",
                [[]]
            )[0]

            metadatas = result.get(
                "metadatas",
                [[]]
            )[0]

            distances = result.get(
                "distances",
                [[]]
            )[0]

            intents = [
                get_intent(metadata)
                for metadata in metadatas
            ]

            top1 = intents[0] if intents else None

            top3 = intents[:3]

            top5 = intents[:5]

            # ------------------------------------------------
            # Accuracy / Recall
            # ------------------------------------------------

            is_top1 = top1 == expected_intent

            is_top3 = expected_intent in top3

            is_top5 = expected_intent in top5

            if is_top1:
                top1_correct += 1

            if is_top3:
                top3_correct += 1

            if is_top5:
                top5_correct += 1

            # ------------------------------------------------
            # Rank / MRR
            # ------------------------------------------------

            expected_rank = None

            for rank, intent in enumerate(
                intents,
                start=1
            ):

                if intent == expected_intent:

                    expected_rank = rank

                    break

            if expected_rank:
                reciprocal_ranks.append(
                    1 / expected_rank
                )
            else:
                reciprocal_ranks.append(0)

            # ------------------------------------------------
            # Console output
            # ------------------------------------------------

            status = (
                "PASS"
                if is_top1
                else "FAIL"
            )

            print(
                f"[{number:03d}/{total}] "
                f"{status:4} | "
                f"Expected: "
                f"{expected_intent:35} | "
                f"Top-1: "
                f"{str(top1):35}"
            )

            # ------------------------------------------------
            # Save result
            # ------------------------------------------------

            rows.append({

                "number":
                    number,

                "query":
                    query,

                "expected_intent":
                    expected_intent,

                "top1_intent":
                    top1,

                "top3_intents":
                    " | ".join(
                        str(x)
                        for x in top3
                    ),

                "top5_intents":
                    " | ".join(
                        str(x)
                        for x in top5
                    ),

                "expected_rank":
                    expected_rank or "",

                "top1_distance":
                    distances[0]
                    if distances
                    else "",

                "top1_pass":
                    "PASS"
                    if is_top1
                    else "FAIL",

                "top3_pass":
                    "PASS"
                    if is_top3
                    else "FAIL",

                "top5_pass":
                    "PASS"
                    if is_top5
                    else "FAIL",
            })

        except Exception as error:

            print(
                f"[{number:03d}/{total}] "
                f"ERROR | {query}"
            )

            print(
                f"          {error}"
            )

            rows.append({

                "number":
                    number,

                "query":
                    query,

                "expected_intent":
                    expected_intent,

                "top1_intent":
                    "",

                "top3_intents":
                    "",

                "top5_intents":
                    "",

                "expected_rank":
                    "",

                "top1_distance":
                    "",

                "top1_pass":
                    "ERROR",

                "top3_pass":
                    "ERROR",

                "top5_pass":
                    "ERROR",
            })

    # ========================================================
    # METRICS
    # ========================================================

    elapsed = (
        time.perf_counter()
        - start_time
    )

    top1_accuracy = (
        top1_correct / total * 100
    )

    top3_recall = (
        top3_correct / total * 100
    )

    top5_recall = (
        top5_correct / total * 100
    )

    mrr = (
        sum(reciprocal_ranks)
        / total
    )


    # ========================================================
    # SUMMARY
    # ========================================================

    print()

    print("=" * 80)
    print("FINAL RESULTS")
    print("=" * 80)

    print(
        f"Total queries : "
        f"{total}"
    )

    print(
        f"Top-1 accuracy: "
        f"{top1_accuracy:.2f}% "
        f"({top1_correct}/{total})"
    )

    print(
        f"Top-3 recall  : "
        f"{top3_recall:.2f}% "
        f"({top3_correct}/{total})"
    )

    print(
        f"Top-5 recall  : "
        f"{top5_recall:.2f}% "
        f"({top5_correct}/{total})"
    )

    print(
        f"MRR           : "
        f"{mrr:.4f}"
    )

    print(
        f"Time          : "
        f"{elapsed:.2f} seconds"
    )


    # ========================================================
    # FAILURES
    # ========================================================

    failures = [
        row
        for row in rows
        if row["top1_pass"] == "FAIL"
    ]

    print()

    print("=" * 80)
    print("TOP-1 FAILURES")
    print("=" * 80)

    if not failures:

        print(
            "No Top-1 failures. Excellent!"
        )

    else:

        for row in failures:

            print()

            print(
                f"Query    : "
                f"{row['query']}"
            )

            print(
                f"Expected : "
                f"{row['expected_intent']}"
            )

            print(
                f"Top-1    : "
                f"{row['top1_intent']}"
            )

            print(
                f"Top-3    : "
                f"{row['top3_intents']}"
            )

            print(
                f"Rank     : "
                f"{row['expected_rank']}"
            )


    # ========================================================
    # CSV REPORT
    # ========================================================

    report_path = (
        PROJECT_ROOT
        / "tests"
        / "retrieval_results.csv"
    )

    with report_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=rows[0].keys()
        )

        writer.writeheader()

        writer.writerows(rows)


    print()

    print(
        f"Detailed report saved to:"
    )

    print(
        report_path
    )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    evaluate()