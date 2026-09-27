from .rules import classify_by_rules
from .embeddings import classify_by_embeddings
from .models import RouteResult
from .context import resolve_intent

from chatbot.entities.extractor import EntityExtractor


RULE_CONFIDENCE_THRESHOLD = 0.50


class RoutingService:

    @staticmethod
    def classify(query: str) -> RouteResult:

        # ====================================================
        # Step 1: CANDIDATE GENERATION
        # ====================================================
        # Get candidates from both rule engine and embeddings.
        # The rule engine is tried first; if its confidence is
        # below the threshold, embeddings provide the candidate.

        result = classify_by_rules(query)

        if result.confidence < RULE_CONFIDENCE_THRESHOLD:
            result = classify_by_embeddings(query)

        # ====================================================
        # Step 2: CONTEXT RESOLUTION (FINAL ARBITER)
        # ====================================================
        # The context resolver examines the query for strong
        # intent-bearing context and may override the candidate.
        #
        # This runs AFTER both rule and embedding classification,
        # so it cannot be bypassed by early returns or fallback.

        if result.intent is not None:
            resolved_intent, resolved_confidence = resolve_intent(
                query,
                result.intent,
                result.confidence,
            )
            result.intent = resolved_intent
            result.confidence = resolved_confidence

        # ====================================================
        # Step 3: ENTITY EXTRACTION
        # ====================================================

        if result.intent is not None:
            result.entities = EntityExtractor.extract(
                query,
                result.intent
            )

        return result