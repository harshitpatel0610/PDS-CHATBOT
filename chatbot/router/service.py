from .rules import classify_by_rules
from .embeddings import classify_by_embeddings
from .models import RouteResult

from chatbot.entities.extractor import EntityExtractor


RULE_CONFIDENCE_THRESHOLD = 0.50


class RoutingService:

    @staticmethod
    def classify(query: str) -> RouteResult:

        # Step 1: Try the rule engine
        result = classify_by_rules(query)

        # Step 2: If rule confidence is low, use embeddings
        if result.confidence < RULE_CONFIDENCE_THRESHOLD:
            result = classify_by_embeddings(query)

        # Step 3: Extract entities if an intent was found
        if result.intent is not None:
            result.entities = EntityExtractor.extract(
                query,
                result.intent
            )

        return result