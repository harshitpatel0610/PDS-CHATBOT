from rapidfuzz import fuzz

from .models import RouteResult
from .embeddings import PDS_INTENTS


# ============================================================
# INTENT-SPECIFIC PHRASES
# ============================================================

STRONG_ACTION_PHRASES = {

    "ration_card_apply": [

        "get a ration card",
        "want a ration card",
        "need a ration card",
        "get new ration card",
        "want a new ration card",
        "need a new ration card",

        "want to get a ration card",
        "need to get a ration card",
        "how to get a ration card",
        "how can i get a ration card",
        "what do i need to do to get a ration card",
        "i want to get a ration card",
        "i need to get a ration card",

        "obtain a ration card",
        "want to obtain a ration card",
        "need to obtain a ration card",
        "how to obtain a ration card",

        "apply for a ration card",
        "apply for a new ration card",
        "want to apply for a ration card",
        "need to apply for a ration card",
        "how to apply for a ration card",
        "how can i apply for a ration card",

        "register for a ration card",
        "ration card registration",
        "ration card application",

        "ration card banwana",
        "ration card banwana hai",
        "naya ration card",
        "naya ration card banwana",
        "naya card banwana",
        "ration card ke liye apply",
        "ration card apply karna",
        "ration card ke liye apply karna",
    ],


    "ration_card_download": [

        "download ration card",
        "download my ration card",
        "ration card pdf",
        "download digital ration card",
        "print ration card",
        "digital copy of ration card",
        "soft copy of ration card",

    ],


    "ration_card_duplicate": [

        "lost ration card",
        "lost my ration card",
        "duplicate ration card",
        "damaged ration card",
        "replace ration card",
        "replacement ration card",
        "reissue ration card",
        "ration card kho gaya",
        "ration card damage ho gaya",

    ],
}


# ============================================================
# ONLINE / OFFLINE INTENT
# ============================================================
#
# IMPORTANT:
# These phrases describe the METHOD of application.
#
# If a query contains:
#
# "apply" + "office"
# "apply" + "online"
# "apply" + "offline"
# "apply" + "physical form"
#
# then ONLINE/OFFLINE should win over ration_card_apply.
#
# ============================================================

ONLINE_OFFLINE_PHRASES = [

    # Online
    "apply online",
    "apply for ration card online",
    "apply online for ration card",
    "can i apply online",
    "can i apply for ration card online",
    "can i apply for a ration card online",
    "is online application available",
    "is ration card application available online",
    "ration card application online",
    "ration card online application",
    "online ration card application",
    "online application for ration card",
    "apply from home",
    "apply for ration card from home",
    "can i apply from home",
    "can i apply for a ration card from home",
    "ghar baithe",
    "ghar baithe ration card",
    "ghar baithe ration card apply",

    # Offline
    "apply offline",
    "apply for ration card offline",
    "apply offline for ration card",
    "can i apply offline",
    "can i apply for ration card offline",
    "can i apply for a ration card offline",
    "is offline application available",
    "is ration card application available offline",
    "ration card offline application",
    "offline ration card application",
    "offline application for ration card",

    # Online vs Offline
    "online or offline",
    "online vs offline",
    "online or offline application",
    "ration card online or offline",
    "ration card application online or offline",
    "is ration card application online or offline",
    "can i apply online or offline",
    "can i apply for ration card online or offline",

    # Office
    "visit office",
    "visit an office",
    "go to office",
    "go to an office",
    "visit the office",
    "go to the office",
    "office visit",
    "office required",
    "office is required",
    "need to visit office",
    "need to visit an office",
    "do i need to visit the office",
    "do i need to visit an office",
    "do i have to visit the office",
    "do i have to visit an office",
    "do i have to go to the office",
    "do i have to go to an office",
    "is it mandatory to visit the office",
    "is it mandatory to visit an office",
    "without visiting the office",
    "without visiting an office",

    # Physical submission
    "physical form",
    "physical ration card form",
    "physical submission",
    "submit physical form",
    "submit the physical form",
    "submit physical ration card form",
    "physical form at an office",
    "submit form at office",
    "submit the form at office",
    "submit application at office",

    # CSC / Government portal
    "csc center",
    "csc centre",
    "government portal",
    "online portal",
    "ration card portal",
    "apply through csc",
    "apply at csc",
    "submit at csc",

    # Hindi / Hinglish
    "office jana padega",
    "office jaana padega",
    "office jana hai",
    "office jaana hai",
    "office jana zaroori hai",
    "office jaana zaroori hai",
    "kya office jana padega",
    "kya office jaana padega",
    "ghar baithe ration card ban sakta hai",
    "ghar baithe ration card banwana",
    "online ration card ban sakta hai",
    "ration card online banwana",
    "ration card offline banwana",
]


# ============================================================
# METHOD SIGNALS
# ============================================================

ONLINE_OFFLINE_SIGNALS = [

    "online",
    "offline",
    "office",
    "csc",
    "portal",
    "physical",
    "ghar baithe",
    "home",
    "visit",
    "visiting",
    "submit at",
    "submission",
]


# ============================================================
# NEGATIVE / EXCLUSION SIGNALS
# ============================================================

ONLINE_OFFLINE_NEGATIVES = [

    "download",
    "pdf",
    "print",
    "lost",
    "duplicate",
    "damaged",
    "replacement",
    "reissue",
]


# ============================================================
# NORMALIZE
# ============================================================

def normalize(text: str) -> str:

    return " ".join(
        text.lower()
        .strip()
        .split()
    )


# ============================================================
# CHECK ONLINE / OFFLINE INTENT
# ============================================================

def is_online_offline_query(query: str) -> bool:

    query = normalize(query)

    # --------------------------------------------------------
    # Explicit bypass for link/url requests
    # --------------------------------------------------------
    if any(word in query for word in ["url", "link", "website"]):
        return False

    # --------------------------------------------------------
    # Explicit phrase match
    # --------------------------------------------------------

    for phrase in ONLINE_OFFLINE_PHRASES:

        if phrase in query:
            return True


    # --------------------------------------------------------
    # Strong combination signals
    # --------------------------------------------------------
    #
    # Example:
    #
    # "Do I have to go to an office to apply for a ration card?"
    #
    # Contains:
    # apply + office
    #
    # Therefore -> online/offline
    # --------------------------------------------------------

    has_apply = any(
        phrase in query
        for phrase in [
            "apply",
            "application",
            "banwana",
            "banwana hai",
            "banega",
            "registration",
            "register",
        ]
    )

    has_method = any(
        signal in query
        for signal in ONLINE_OFFLINE_SIGNALS
    )

    if has_apply and has_method:
        return True


    # --------------------------------------------------------
    # Question about requirement to visit
    # --------------------------------------------------------

    office_question_words = [
        "do i",
        "do i have",
        "do i need",
        "do i have to",
        "is it mandatory",
        "is it necessary",
        "can i",
        "where",
        "how",
    ]

    has_office = (
        "office" in query
        or "visit" in query
        or "visiting" in query
        or "csc" in query
    )

    has_question_structure = any(
        phrase in query
        for phrase in office_question_words
    )

    if has_office and has_question_structure:

        if "ration card" in query:
            return True


    return False


# ============================================================
# RULE-BASED CLASSIFIER
# ============================================================

def classify_by_rules(query: str) -> RouteResult:

    query = normalize(query)


    # ========================================================
    # STEP 1
    # EXPLICIT ONLINE/OFFLINE OVERRIDE
    # ========================================================
    #
    # This MUST happen before normal scoring.
    #
    # Otherwise:
    #
    # "Do I have to go to an office to apply for a ration card?"
    #
    # would match:
    #
    # ration_card_apply
    #
    # because of "apply for ration card".
    #
    # ========================================================

    if is_online_offline_query(query):

        online_offline_intent = next(
            (
                intent
                for intent in PDS_INTENTS
                if intent["intent"] == "ration_card_online_offline"
            ),
            None
        )

        if online_offline_intent:

            return RouteResult(
                is_pds=True,
                intent="ration_card_online_offline",
                confidence=1.0
            )


    # ========================================================
    # STEP 2
    # NORMAL INTENT SCORING
    # ========================================================

    best_intent = None
    best_score = 0.0


    for intent in PDS_INTENTS:

        score = 0.0

        intent_name = intent["intent"]


        # ====================================================
        # KEYWORDS
        # ====================================================

        for keyword in intent.get("keywords", []):

            keyword = normalize(keyword)

            if not keyword:
                continue

            if keyword in query:

                if len(keyword) <= 3:

                    score += 10

                elif len(keyword.split()) >= 3:

                    score += 40

                elif len(keyword.split()) == 2:

                    score += 30

                else:

                    score += 20


        # ====================================================
        # PATTERNS
        # ====================================================

        for pattern in intent.get("patterns", []):

            pattern = normalize(pattern)

            if not pattern:
                continue

            similarity = max(
                fuzz.partial_ratio(query, pattern),
                fuzz.token_set_ratio(query, pattern)
            )

            pattern_score = similarity * 0.4

            if pattern_score > score:

                score = pattern_score


        # ====================================================
        # EXAMPLES
        # ====================================================

        for example in intent.get("examples", []):

            example = normalize(example)

            if not example:
                continue

            similarity = fuzz.token_set_ratio(
                query,
                example
            )

            example_score = similarity * 0.4

            if example_score > score:

                score = example_score


        # ====================================================
        # NEGATIVE PATTERNS
        # ====================================================

        for negative in intent.get("negative_patterns", []):

            negative = normalize(negative)

            if negative and negative in query:

                score -= 30


        # ====================================================
        # STRONG ACTION BOOST
        # ====================================================

        for phrase in STRONG_ACTION_PHRASES.get(
            intent_name,
            []
        ):

            phrase = normalize(phrase)

            if phrase in query:

                score += 50
                break


        # ====================================================
        # PRIORITY
        # ====================================================

        score += intent.get("priority", 0)


        # ====================================================
        # BEST INTENT
        # ====================================================

        if score > best_score:

            best_score = score
            best_intent = intent


    # ========================================================
    # CONFIDENCE
    # ========================================================

    confidence = min(
        best_score / 100,
        1.0
    )


    # ========================================================
    # RETURN BEST CANDIDATE
    # ========================================================
    # Return the raw scoring result. Context resolution is
    # handled by the resolver in service.py, which sits above
    # both the rule engine and the embedding classifier.

    if best_intent:
        return RouteResult(
            is_pds=True,
            intent=best_intent["intent"],
            confidence=confidence
        )

    return RouteResult(
        is_pds=False,
        intent=None,
        confidence=0.0
    )