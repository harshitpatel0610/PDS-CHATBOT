from chatbot.services.chat_service import ChatService


class DialogueManager:

    @staticmethod
    def process(session, message):

        session.history.append({
            "role": "user",
            "message": message
        })

        result = ChatService.process(session, message)

        session.history.append({
            "role": "assistant",
            "message": result["response"]
        })

        return result["response"]