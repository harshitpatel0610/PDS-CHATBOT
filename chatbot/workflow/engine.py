from .manager import WorkflowManager
from chatbot.services.rag_service import RAGService

class WorkflowEngine:

    @staticmethod
    def process(session):

        print(">>> WorkflowEngine.process()")

        if WorkflowManager.is_complete(session):

            print(">>> COMPLETE")
            
            # The message is the last user message in the session history
            last_message = session.history[-1]["message"] if session.history else ""

            return {
                "completed": True,
                "response": RAGService.generate_response(session, last_message)
            }

        print(">>> NOT COMPLETE")

        question = WorkflowManager.next_question(session)

        return {
            "completed": False,
            "response": question
        }