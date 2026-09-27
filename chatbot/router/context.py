"""
Context-aware intent resolution for the PDS chatbot router.

This module provides centralized, testable context detectors and
a final intent resolver that sits ABOVE both the rule-based and
embedding-based classifiers.

Architecture:
    USER QUERY
        |
        v
    NORMALIZATION
        |
    +---+---+
    |       |
    v       v
  RULES   EMBEDDINGS
    |       |
    +---+---+
        |
        v
  CONTEXT RESOLVER  <-- this module
        |
        v
    FINAL INTENT

The context resolver applies a deterministic intent hierarchy ONLY when
there is strong contextual evidence in the query. It does NOT blindly
override based on single keywords.

Hierarchy (applied only when strong context is detected):
    Eligibility > Documents Required > Online/Offline > Application > Other
"""

import re


# ============================================================
# NORMALIZATION
# ============================================================

# Common Aadhaar spelling variants -> canonical form
_AADHAAR_VARIANTS = re.compile(
    r'\b(aadhaar|aadhar|adhaar|aadhr|adhar|aadhar)\b',
    re.IGNORECASE
)

def normalize_query(text: str) -> str:
    """Normalize query for context detection.
    
    - lowercase
    - collapse whitespace
    - strip punctuation that breaks word boundaries
    - normalize Aadhaar variants
    """
    text = text.lower().strip()
    text = _AADHAAR_VARIANTS.sub('aadhaar', text)
    # Normalize "nhi" -> "nahi" for Hindi negation
    text = re.sub(r'\bnhi\b', 'nahi', text)
    # Collapse whitespace
    text = ' '.join(text.split())
    # Remove trailing punctuation from words for cleaner matching
    # but keep the full text for phrase matching
    return text


# ============================================================
# WORD BOUNDARY HELPERS
# ============================================================

def _has_word(query: str, word: str) -> bool:
    """Check if word appears as a complete word (not substring)."""
    return bool(re.search(r'\b' + re.escape(word) + r'\b', query))


def _has_any_word(query: str, words: list) -> bool:
    """Check if any word from the list appears as a complete word."""
    return any(_has_word(query, w) for w in words)


def _has_phrase(query: str, phrase: str) -> bool:
    """Check if phrase appears in query."""
    return phrase in query


def _has_any_phrase(query: str, phrases: list) -> bool:
    """Check if any phrase appears in query."""
    return any(phrase in query for phrase in phrases)


# ============================================================
# CONTEXT DETECTORS
# ============================================================
# Each detector returns True only when there is STRONG contextual
# evidence for that intent category. Broad single-keyword matches
# are explicitly avoided to prevent false positives.

def detect_eligibility_context(query: str) -> bool:
    """Detect strong eligibility/qualification context.
    
    POSITIVE examples:
        "Who is eligible for APL ration card?"
        "Who can get a BPL ration card?"
        "Am I eligible for a ration card?"
        "What are the eligibility criteria?"
        "Who qualifies for BPL?"
        "Can I qualify for APL?"
    
    NEGATIVE examples (must NOT match):
        "Who is the ration card officer?"       -> contact_admin
        "Who should I contact?"                 -> pds_helpline  
        "Who handles complaints?"               -> file_complaint
        "How can an eligible person apply?"     -> ration_card_apply
        "What documents should an eligible applicant submit?" -> documents_required
    """
    q = normalize_query(query)
    
    # Strong eligibility phrases (multi-word, unambiguous)
    strong_phrases = [
        "eligibility criteria",
        "eligibility requirement",
        "am i eligible",
        "who qualifies",
        "who is eligible",
        "who are eligible",
        "who gets a card",
        "who gets ration",
        "can i qualify",
        "do i qualify",
        "qualify for ration",
        "qualify for a ration",
        "qualify for apl",
        "qualify for bpl",
        "qualify for aay",
        "qualify for phh",
        "eligible for apl",
        "eligible for bpl",
        "eligible for aay",
        "eligible for phh",
        "eligible for ration",
        "eligible for a ration",
        "eligible for an apl",
        "eligible for an bpl",
        "eligible hai",
        "kon eligible",
        "kaun eligible",
        "koun eligible",
    ]
    
    if _has_any_phrase(q, strong_phrases):
        return True
    
    # "who can" + ration-card-related verb (get/apply/receive)
    # This catches "Who can get an APL ration card?" and
    # "Who can apply for BPL?" but NOT "Who can I contact?"
    who_can_match = re.search(
        r'\bwho\s+(?:can|is\s+allowed\s+to|is\s+permitted\s+to)\s+'
        r'(?:get|apply|receive|obtain|have|avail)',
        q
    )
    if who_can_match:
        return True
    
    # "allowed to apply" pattern
    if _has_phrase(q, "allowed to apply") or _has_phrase(q, "allowed to get"):
        return True
    
    # Hinglish: "kon apply kar sakta" (who can apply)
    if re.search(r'\bkon\b.*\bapply\b.*\bsakta\b', q):
        return True
    if re.search(r'\bkaun\b.*\bapply\b.*\bsakta\b', q):
        return True
        
    # "Can I apply?" -> Am I eligible?
    # Exclude: "Can I apply online?" (channel), "How can I apply?" (process)
    if _has_phrase(q, "can i apply") or _has_phrase(q, "can we apply"):
        if not _has_any_word(q, ["how", "where", "online", "offline", "home", "csc", "portal", "office", "without", "bina"]):
            # If it's a document question like "Can I apply without Aadhaar?", let documents win.
            if not detect_document_requirement_context(query):
                return True
    
    # "eligibility" as a standalone word, but ONLY if the query is
    # actually asking ABOUT eligibility, not mentioning it incidentally.
    # Require "eligibility" + ration/card context, but NOT if the primary
    # verb is about documents/submit/apply-process.
    if _has_word(q, "eligibility"):
        # Exclude: "What documents should an eligible applicant submit?"
        if not _has_any_word(q, ["document", "documents", "submit", "upload", "proof"]):
            return True
    
    return False


def detect_document_requirement_context(query: str) -> bool:
    """Detect queries asking WHAT documents are needed (requirements).
    
    POSITIVE examples:
        "What documents are required for APL?"
        "Is Aadhaar mandatory for ration card?"
        "Can I apply without Aadhaar?"
        "What proof is needed?"
        "Aadhaar nahi hai to apply kar sakte hai?"
    
    NEGATIVE examples (must NOT match):
        "Where can I submit my documents?"      -> ration_card_apply
        "How do I upload documents online?"      -> ration_card_apply  
        "Can I update my Aadhaar document?"      -> ration_card_update
        "What happens after document verification?" -> ration_card_status
        "Which office verifies my documents?"    -> contact_admin
    
    Key distinction: DOCUMENT REQUIREMENT != DOCUMENT MENTION.
    The query must be asking about which documents are needed or
    whether a specific document is mandatory, not about the process
    of submitting/uploading/updating documents.
    """
    q = normalize_query(query)
    
    # Exclude document-process queries early.
    # These mention documents but are asking about process, not requirements.
    process_verbs = [
        "submit", "upload", "update", "verify", "verification",
        "download", "print", "correct", "correction"
    ]
    if _has_any_word(q, process_verbs):
        return False
    
    # "after document" -> status query, not requirement
    if _has_phrase(q, "after document"):
        return False
    
    # "which office" / "where" + documents -> location, not requirement
    if _has_any_phrase(q, ["which office", "where can i"]):
        if _has_any_word(q, ["document", "documents"]):
            return False
    
    # Strong document requirement phrases
    strong_phrases = [
        "documents required",
        "documents needed",
        "document required",
        "document needed",
        "documents are required",
        "documents are needed",
        "what documents",
        "which documents",
        "what proof",
        "which proof",
        "what paperwork",
        "proof needed",
        "proof required",
        "paperwork needed",
        "paperwork required",
        "kya document chahiye",
        "kaun se document",
        "kaun se kagaz",
        "kagaz lagte",
        "document chahiye",
    ]
    
    if _has_any_phrase(q, strong_phrases):
        return True
    
    # Aadhaar + mandatory/compulsory/required/without/need
    if _has_any_word(q, ["aadhaar", "adhaar"]):
        if _has_any_word(q, ["mandatory", "compulsory", "required", "zaroori", "jaruri", "need", "chahiye"]):
            return True
        # "without Aadhaar" / "don't have Aadhaar" / "Aadhaar nahi hai"
        if _has_any_phrase(q, [
            "without aadhaar", "bina aadhaar",
            "don't have aadhaar", "do not have aadhaar",
            "aadhaar nahi hai", "aadhaar nahi he",
        ]):
            return True
    
    return False


def detect_online_offline_context(query: str) -> bool:
    """Detect queries asking about application CHANNEL (online vs offline).
    
    POSITIVE examples:
        "Can I apply online or offline?"
        "Is the application online or offline?"
        "Do I need to visit the office?"
        "ration card online banega ya offline?"
    
    NEGATIVE examples (must NOT match):
        "How can I apply online?"               -> ration_card_apply (process)
        "How can I apply offline?"              -> ration_card_apply (process)
        "Where can I apply online?"             -> ration_card_apply (process)
    
    Key distinction: Asking WHETHER online/offline is available (channel)
    vs asking HOW to do it (process).
    """
    q = normalize_query(query)
    
    # "how" queries are asking about process, not channel
    if _has_any_word(q, ["how", "kaise"]):
        return False
    
    # "where can I apply online/offline" -> user wants to know the channel location
    if re.search(r'\bwhere\b.*\bapply\b.*\b(online|offline)\b', q):
        return True
    
    # "what is the online application process" -> process
    if _has_any_phrase(q, ["application process", "apply process"]):
        return False
    
    # Strong channel phrases
    channel_phrases = [
        "online or offline",
        "online vs offline",
        "offline or online",
        "online ya offline",
        "offline ya online",
        "online banega ya offline",
        "offline banega ya online",
        "is the application online",
        "is application online",
        "is ration card application online",
        "is ration card application available online",
        "is ration card application available offline",
        "is online application available",
        "is offline application available",
    ]
    
    if _has_any_phrase(q, channel_phrases):
        return True
    
    # "Can I apply online/offline?" without "how" -> channel question
    if re.search(r'\bcan\s+i\s+apply\s+(online|offline)\b', q):
        return True
    
    # Office visit questions: "Do I need to visit the office?"
    office_visit = re.search(
        r'\b(do\s+i\s+(?:need|have)\s+to|is\s+it\s+(?:mandatory|necessary)\s+to)\s+'
        r'(?:visit|go\s+to)',
        q
    )
    if office_visit and _has_any_word(q, ["office", "csc"]):
        return True
    
    # CSC/portal questions (without how)
    if _has_any_phrase(q, ["through csc", "at csc", "through a csc", "at a csc"]):
        return True
    if _has_any_phrase(q, ["government portal", "online portal"]):
        if not _has_any_word(q, ["how", "kaise"]):
            return True
    
    # Physical form / from home
    if _has_any_phrase(q, ["physical form", "from home", "ghar baithe"]):
        if not _has_any_word(q, ["how", "kaise"]):
            return True
    
    # Hindi: "office jana padega" / "office jaana padega"
    if _has_any_phrase(q, ["office jana", "office jaana"]):
        return True
    
    return False


def detect_application_context(query: str) -> bool:
    """Detect queries asking about HOW to apply (the application process).
    
    POSITIVE examples:
        "How can I apply for APL?"
        "How do I apply for a ration card?"
        "What is the application process?"
        "ration card ke liye kaha apply kare?"
    
    NEGATIVE examples (must NOT match):
        "Who can apply for APL?"                -> eligibility
        "Can I apply without Aadhaar?"          -> documents_required
        "Can I apply online or offline?"        -> online/offline
    """
    q = normalize_query(query)
    
    # "how" + apply/application
    if _has_any_word(q, ["how", "kaise"]):
        if _has_any_word(q, ["apply", "application", "banwana", "banwaye"]):
            return True
    
    # "where to apply" / "kaha apply kare"
    if re.search(r'\b(where|kaha|kahan)\b.*\bapply\b', q):
        if not re.search(r'\b(online|offline)\b', q):
            return True
    
    # "application process" / "application procedure"
    if _has_any_phrase(q, ["application process", "application procedure", "apply process"]):
        return True
    
    return False


# ============================================================
# CONTEXT RESOLVER
# ============================================================

# Intents that participate in the contextual hierarchy.
# Other intents (contact_admin, ration_card_update, etc.) are
# NOT overridden by the hierarchy and pass through unchanged.
_CONTESTABLE_INTENTS = {
    "ration_card_types",
    "ration_card_apply",
    "ration_card_eligibility",
    "ration_card_online_offline",
    "documents_required",
}


def resolve_intent(
    query: str,
    candidate_intent: str,
    candidate_confidence: float,
) -> tuple:
    """Apply contextual resolution to the candidate intent.
    
    This function is the FINAL arbiter in the routing pipeline.
    It examines the query for strong contextual signals and may
    override the candidate intent when there is clear evidence
    of a different primary intent.
    
    The hierarchy is applied only when:
    1. The candidate intent is one of the contestable intents
    2. There is strong contextual evidence for a different intent
    
    Non-contestable intents (e.g., ration_card_update, contact_admin,
    file_complaint) are NEVER overridden.
    
    Returns:
        (intent, confidence) tuple
    """
    # If the candidate is not contestable, don't touch it.
    # This preserves ration_card_update, contact_admin, file_complaint, etc.
    if candidate_intent not in _CONTESTABLE_INTENTS:
        return candidate_intent, candidate_confidence
    
    # Detect contexts
    has_eligibility = detect_eligibility_context(query)
    has_documents = detect_document_requirement_context(query)
    has_online_offline = detect_online_offline_context(query)
    has_application = detect_application_context(query)
    
    # Apply hierarchy: Eligibility > Documents > Online/Offline > Application
    # Only override if the detected context differs from the candidate.
    
    if has_eligibility:
        return "ration_card_eligibility", max(candidate_confidence, 0.95)
    
    if has_documents:
        return "documents_required", max(candidate_confidence, 0.95)
    
    if has_online_offline:
        return "ration_card_online_offline", max(candidate_confidence, 0.95)
    
    if has_application:
        return "ration_card_apply", max(candidate_confidence, 0.95)
        
    # Action Precedence: If the candidate is an informational type intent
    # but the user is using action words, it's actually an apply/action query.
    if candidate_intent in ["ration_card_types", "ration_quota", "ration_items_list"]:
        q = normalize_query(query)
        # Prevent override if asking "which" category
        if _has_any_word(q, ["which", "kaun sa", "konsa", "kounsa", "what type", "kya type", "which category"]):
            return candidate_intent, candidate_confidence
            
        action_words = ["apply", "get", "banwana", "register", "create", "new"]
        if _has_any_word(q, action_words):
            return "ration_card_apply", max(candidate_confidence, 0.95)
    
    # No strong context detected -> keep the candidate as-is
    return candidate_intent, candidate_confidence
