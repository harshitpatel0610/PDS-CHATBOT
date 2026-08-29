from chatbot.router.router import route
from chatbot.entities.extractor import EntityExtractor
from chatbot.workflow.engine import WorkflowEngine


class ChatService:

    @staticmethod
    def process(session, message):
        import time
        start_total = time.perf_counter()

        # Detect intent only if we don't already have one
        if session.current_intent is None:
            result = route(message)
            if not result.is_pds:
                return {
                    "success": False,
                    "response": "Sorry, I can only answer Public Distribution System (PDS) related questions."
                }
            session.current_intent = result.intent
            session.confidence = result.confidence

        # Extract entities
        t0 = time.perf_counter()
        entities = EntityExtractor.extract(
            message,
            session.current_intent
        )
        t_entities = time.perf_counter() - t0

        t0 = time.perf_counter()
        for entity in entities:
            if entity.entity_type not in session.entities:
                session.entities[entity.entity_type] = entity.value
        t_session = time.perf_counter() - t0

        # Run workflow
        workflow = WorkflowEngine.process(session)
        t_total = time.perf_counter() - start_total

        if workflow["completed"]:
            print(f"\n--- TIMING BREAKDOWN ---")
            print(f"Entity extraction: {t_entities*1000:.2f} ms")
            print(f"Session retrieval/update: {t_session*1000:.2f} ms")
            
            timing = getattr(session, "timing", {})
            print(f"Retrieval level determination: {timing.get('retrieval_level', 0):.2f} ms")
            print(f"ChromaDB retrieval: {timing.get('chromadb', 0):.2f} ms")
            print(f"Context construction: {timing.get('context', 0):.2f} ms")
            print(f"Gemini API: {timing.get('gemini', 0):.2f} ms")
            print(f"Response construction: {timing.get('response_construct', 0):.2f} ms")
            
            print(f"TOTAL: {t_total*1000:.2f} ms")
            print("------------------------\n")

        return {
            "success": True,
            "intent": session.current_intent,
            "entities": session.entities,
            "response": workflow["response"],
            "completed": workflow["completed"]
        }