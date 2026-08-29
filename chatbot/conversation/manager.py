from chatbot.router.router import route

from .store import ConversationStore
from .session import ConversationSession


class ConversationManager:

    @staticmethod
    def process(session_id: str, query: str):

        # Load/Create session
        session = ConversationStore.get(session_id)

        # Save user message
        session.add_message("user", query)

        # Route query
        result = route(query)
        print(result)

        # Update intent
        if result.intent:
            session.set_intent(
                result.intent,
                result.confidence
            )

        # Save entities
        for entity in result.entities:

            session.add_entity(
                entity.entity_type,
                entity.value
            )

        # Save session
        ConversationStore.save(session)

        return session, result